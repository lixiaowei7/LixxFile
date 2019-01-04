# <Lixx_TIF, a model for reading and writing tif files.>
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

import struct
import numpy as np

from Lixx_file import LixxFile

tags = {
    256: "ImageWidth",
    257: "ImageLength",
    258: "BitsPerSample",
    259: "Compression",
    262: "PhotometricInterpretation",
    273: "StripOffsets",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    279: "StripByteCounts",
    284: "PlanarConfiguration",
    339: "SampleFormat",
    33550: "ModelPixelScaleTag",
    33922: "ModelTiepointTag",
    34735: "GeoKeyDirectoryTag",
    34736: "GeoDoubleParamsTag",
    34737: "GeoAsciiParamsTag"
}

types = {
    1: "BYTE",
    2: "ASCII",
    3: "SHORT",
    4: "LONG",
    5: "RATIONAL",
    6: "SBYTE",
    7: "UNDEFINED",
    8: "SSHORT",
    9: "SLONG",
    10: "SRATIONAL",
    11: "FLOAT",
    12: "DOUBLE"
}

class LixxTIF(LixxFile):
    """TIFF Revision 6.0"""

    def __init__(self, path, mode="rb+"):
        super(LixxTIF, self).__init__(path, mode)
        self.byte_order, self.first_ifd = self._header()
        self.ifds = self._ifds()

        self.strips = []
        # image array
        self.img = None
        # pixel pointers array
        self.pointers = None

        # sign pixel changed or not
        self.sign = False

    def __del__(self):
        self.close()
    
    def close(self):
        self.fp.close()

    def _header(self):
        fp = self.fp

        fp.seek(0, 0)
        byte_order = fp.read(2)
        arbitary_number = fp.read(2)
        first_ifd = fp.read(4)

        if byte_order == b'\x49\x49':
            byte_order = "little"
        elif byte_order == b'\x4D\x4D':
            byte_order = "big"
        else:
            raise ValueError

        if int.from_bytes(arbitary_number, byteorder=byte_order) != 42:
            raise ValueError

        return byte_order, first_ifd

    def int_from_bytes(self, b):
        byte_order = self.byte_order
        return int.from_bytes(b, byteorder=byte_order)

    def _ifds(self):
        fp = self.fp
        byte_order = self.byte_order
        first_ifd = self.first_ifd
        int_from_bytes = self.int_from_bytes

        ifds = {}
        ifd_num = int_from_bytes(fp.read(2))
        for i in range(ifd_num):
            tag = fp.read(2)

            tmp = {}
            tmp["type"] = int_from_bytes(fp.read(2))
            tmp["count"] = int_from_bytes(fp.read(4))
            tmp["valueOrOffset"] = int_from_bytes(fp.read(4))

            ifds[int_from_bytes(tag)] = tmp

        return ifds

    def __getitem__(self, key):
        ifds = self.ifds

        if key not in ifds:
            raise KeyError(key)
        
        return ifds[key]
    
    def lixx_info(self):
        ifds = self.ifds
        int_from_bytes = self.int_from_bytes

        keys = list(ifds.keys())
        keys.sort()

        res = "{0:<6} {1:<25} {2:<10} {3:<10} {4:<10}\n".format("Tag", "", "Type", "Count", "valueOrOffset")
        for key in keys:
            ifd = ifds[key]
            tag = tags[key] if key in tags else ""
            ifd_type = types[ifd["type"]]
            ifd_count = ifd["count"]
            ifd_valueOrOffset = ifd["valueOrOffset"]
            tmp = "{0:<6} {1:<25} {2:<10} {3:<10} {4:<10}".format(key, tag, ifd_type, ifd_count, ifd_valueOrOffset)
            res += tmp + "\n"

        return res
    
    def scale(self):
        """width, height"""
        width, height = self[256]["valueOrOffset"], self[257]["valueOrOffset"]
        return width, height
    
    def _strips(self):
        if self.strips:
           return self.strips

        fp = self.fp
        strips = self.strips
        int_from_bytes = self.int_from_bytes

        StripOffsets = self[273]
        RowsPerStrip = self[278]
        StripByteCounts = self[279]

        assert RowsPerStrip["count"] == 1
        assert StripByteCounts["count"] == StripOffsets["count"]

        # value
        if StripByteCounts["count"] == 1 and StripOffsets["count"] == 1:
            tmp = {}
            tmp["byteCounts"] = StripByteCounts["valueOrOffset"]
            tmp["offsets"] = StripOffsets["valueOrOffset"]
            strips.append(tmp)
            return strips

        # offset
        stripOffsets = []
        fp.seek(StripOffsets["valueOrOffset"])
        for i in range(StripOffsets["count"]):
            offset = int_from_bytes(fp.read(4))
            stripOffsets.append(offset)
        
        stripByteCounts = []
        fp.seek(StripByteCounts["valueOrOffset"])
        for i in range(StripByteCounts["count"]):
            byteCount = int_from_bytes(fp.read(4))
            stripByteCounts.append(byteCount)

        
        for i in range(len(stripOffsets)):
            tmp = {}
            tmp["byteCounts"] = stripByteCounts[i]
            tmp["offsets"] = stripOffsets[i]
            strips.append(tmp)
        
        return strips

    def _img(self):
        if self.img is not None and self.sign is False:
            return self.img

        fp = self.fp
        strips = self._strips()
        width, height = self.scale()
        int_from_bytes = self.int_from_bytes

        cnt = -1
        img = np.full((height, width), 0, dtype=np.int16)
        pointers = np.full((height, width), 0, dtype=np.uint32)
        for strip in strips:
            offsets = strip["offsets"]
            byteCounts = strip["byteCounts"]

            fp.seek(offsets)
            for i in range(byteCounts // 2):
                cnt += 1
                pixel = int_from_bytes(fp.read(2))
                # print(cnt, cnt // width, cnt % width, pixel)
                img[cnt // width][cnt % width] = pixel
                pointer = offsets + i * 2
                pointers[cnt // width][cnt % width] = pointer

        self.img = img
        self.sign = False
        self.pointers = pointers
        return img
    
    def setPixel(self, h, w, val):
        """val must be signed short(2 bytes)"""
        if self.img is None:
            self._img()

        fp = self.fp
        pointers = self.pointers
        byte_order = self.byte_order

        pointer = pointers[h][w]
        # print()
        # print("setPixel:", h, w, pointer)
        fp.seek(pointer)

        fmt = byte_order == "little" and "<h" or ">h"
        val = struct.pack(fmt, val)
        fp.write(val)

        self.sign = True