# <Lixx_TIF, a model for reading and writing the comments gif files.>
# Copyright (C) <2018>  <Xiaowei Li, Xixiang Zhu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# @Email: Xiaowei Li<lixiaowei7@live.cn>
# @Email: Xixiang Zhu<hixxzhu@gmail.com>

# GIF89a specification: https://www.w3.org/Graphics/GIF/spec-gif89a.txt
# Header
#       7 6 5 4 3 2 1 0        Field Name                    Type
#      +---------------+
#    0 |               |       Signature                     3 Bytes
#      +-             -+
#    1 |               |
#      +-             -+
#    2 |               |
#      +---------------+
#    3 |               |       Version                       3 Bytes
#      +-             -+
#    4 |               |
#      +-             -+
#    5 |               |
#      +---------------+
#
# Logical Screen Descriptor
#       7 6 5 4 3 2 1 0        Field Name                    Type
#      +---------------+
#   0  |               |       Logical Screen Width          Unsigned
#      +-             -+
#   1  |               |
#      +---------------+
#   2  |               |       Logical Screen Height         Unsigned
#      +-             -+
#   3  |               |
#      +---------------+
#   4  | |     | |     |       <Packed Fields>               See below
#      +---------------+
#   5  |               |       Background Color Index        Byte
#      +---------------+
#   6  |               |       Pixel Aspect Ratio            Byte
#      +---------------+
#
#      <Packed Fields>  =      Global Color Table Flag       1 Bit
#                              Color Resolution              3 Bits
#                              Sort Flag                     1 Bit
#                              Size of Global Color Table    3 Bits

import math
import struct

from PIL import Image

class LixxGIF:
    """GIF Revision 89a"""

    def __init__(self, path):
        self.path = path
        self.fp = open(path, "rb+")

        self.s_dataStream = self._p_dataStream()
    
    def _p_dataStream(self):
        """Pointer to the end of global color table."""
        fp = self.fp
        assert fp.read(3) == b"GIF" and fp.read(3) == b"89a"

        fp.seek(10, 0)
        packed_filed = struct.unpack("B", fp.read(1))[0]
        pixel = packed_filed & 7
        # index number of global color table
        size_indexOfGlobalColorTable = 2 ** (pixel + 1)

        return 6 + 7 + size_indexOfGlobalColorTable * 3

class DataSubBlock:
    """
         7 6 5 4 3 2 1 0        Field Name                    Type
        +---------------+
    0   |               |       Block Size                    Byte
        +---------------+
    1   |               |
        +-             -+
    2   |               |
        +-             -+
    3   |               |
        +-             -+
        |               |       Data Values                   Byte
        +-             -+
    up  |               |
        +-   . . . .   -+
    to  |               |
        +-             -+
        |               |
        +-             -+
    255 |               |
        +---------------+
    Block Size - Number of bytes in the Data Sub-block; the size
            must be within 0 and 255 bytes, inclusive.
    Data Values - Any 8-bit value. There must be exactly as many
            Data Values as specified by the Block Size field.
    """

    def __init__(self, content):
        if type(content) == bytes:
            self.content = content
        elif type(content) == str:
            self.content = content.encode("utf-8")
        else:
            raise ValueError("Content type is not in (bytes, str).")

    def subBlock(self):
        """encode"""
        content = self.content

        blocks = len(content) // 255
        partial = len(content) % 255

        res = b""
        for i in range(blocks):
            tmp = struct.pack("B", 0xff)
            tmp += content[i * 255 : i * 255 + 255]
            res += tmp
        
        if partial:
            tmp = struct.pack("B", partial)
            tmp += content[blocks * 255:]
            tmp += struct.pack("B", 0x00) * (256 - len(tmp))
            res += tmp
        
        return res
    
    def __str__(self):
        """decode"""
        content = self.content
        assert len(content) % 256 == 0

        blocks = math.ceil(len(content) / 256)
        
        res = b""
        for i in range(blocks):
            num = struct.unpack("B", content[i * 256: i * 256 + 1])[0]
            res += content[i * 256 + 1 : i * 256 + 1 + num]
        
        return res.decode("utf-8")

class GIFCommentExtension(LixxGIF):
    """
         7 6 5 4 3 2 1 0        Field Name                    Type               Value
        +---------------+
    0   |               |       Extension Introducer          Byte               0x21
        +---------------+
    1   |               |       Comment Label                 Byte               0xFE
        +---------------+

        +===============+
        |               |
    N   |               |       Comment Data                  Data Sub-blocks
        |               |
        +===============+

        +---------------+
    0   |               |       Block Terminator              Byte               0x00
        +---------------+ 
    """

    def __init__(self, path):
        super(GIFCommentExtension, self).__init__(path)
        self.comment_offsets = None
        self.extensionIntroducer = struct.pack("B", 0x21)
        self.commentLabel = struct.pack("B", 0xfe)
        self.blockTerminator = struct.pack("B", 0x00)

    def _commentExtension(self, comment):
        extensionIntroducer = self.extensionIntroducer
        commentLabel = self.commentLabel
        blockTerminator = self.blockTerminator

        d_sb = DataSubBlock(comment)
        comment = d_sb.subBlock()

        return extensionIntroducer + commentLabel + comment + blockTerminator
    
    def addComment(self, comment):
        """Add comment to the end of global color table."""
        fp = self.fp
        s_dataStream = self.s_dataStream

        fp.seek(s_dataStream, 0)
        rest = fp.read()

        fp.seek(s_dataStream, 0)
        comment = self._commentExtension(comment)
        fp.write(comment)
        fp.write(rest)

    def parseComments(self):
        """Return comments which next global color table."""
        fp = self.fp
        s_dataStream = self.s_dataStream
        extensionIntroducer = self.extensionIntroducer
        commentLabel = self.commentLabel
        blockTerminator = self.blockTerminator

        fp.seek(s_dataStream, 0)
        res = []
        while True:
            if fp.read(1) != extensionIntroducer or fp.read(1) != commentLabel:
                break
            subBlocks = b""
            while fp.read(1) != blockTerminator:
                fp.seek(-1, 1)
                subBlocks += fp.read(256)
            
            res.append(subBlocks)
        
        # update the num of bytes about comments for cleaning
        offset = 0
        for subBlocks in res:
            offset += len(subBlocks)
        self.comment_offsets = len(res) * 3 + offset

        return [str(DataSubBlock(item)) for item in res]

    def cleanComments(self):
        """Clean all comments which next global color table."""
        fp = self.fp
        s_dataStream = self.s_dataStream
        if self.comment_offsets is None:
            self.parseComment()
        comment_offsets = self.comment_offsets
        
        fp.seek(s_dataStream, 0)
        fp.seek(comment_offsets)
        rest = fp.read()

        fp.seek(s_dataStream, 0)
        fp.write(rest)
        fp.truncate()

        self.comment_offsets = None

if __name__ == "__main__":
    """
        >>> gce = GIFCommentExtension(path)
        >>> # add comment
        >>> gce.addComment("I'm commtents.")
        >>> # get comments
        >>> comments = gce.parseComments()
        >>> # clean comments
        >>> gce.cleanComments()

    """
    pass