# <Lixx_DBF, a model for reading and writing dbf files.>
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

import os
import copy
import struct
import datetime

from Lixx_file import LixxFile

class LixxDBF(LixxFile):
    """A model for reading and writing dbf files."""

    def __init__(self, path):
        super(LixxDBF, self).__init__(path)
        self.path = path
        
        self.f = None
        self.fields = []
        self.numrec = None
        self.fieldnames = None
        self.fieldspecs = None
        self.records = []
        self.write_records = None

        self.offset = 0
        if path:
            try:
                self.f = open(self.path, 'rb+')
                self._read_header()
            except Exception as e:
                self.f = open(self.path, 'wb+')

    def __del__(self):
        self._close()
    
    def __repr__(self):
        string = ""
        records = self.records
        for record in records:
            tmp = []
            for item in record:
                item = item.strip()
                item = type(item) == bytes and item.decode('GBK') or item
                tmp.append(item)
            string += ", ".join(tmp)
            string += "\n"
        return string

    def _close(self):
        if self.write_records and self.write_records != self.records:
            self.lixx_write()

        if self.f:
            self.f.close()
        self.f = None

    def _read(self, f, offset):
        self.offset += offset
        return f.read(offset)

    def _write(self, f, offset):
        pass

    def _read_header(self):
        f = self.f
        fields = self.fields

        numrec, lenheader = struct.unpack('<xxxxLH22x', self._read(f, 32))
        numfields = (lenheader - 33) // 32

        for fieldno in range(numfields):
            name, typ, size, deci = struct.unpack('<11sc4xBB14x', self._read(f, 32))
            name=name.decode('utf-8')
            typ=typ.decode('utf-8')
            name = name.replace('\0', '')
            fields.append((name, typ, size, deci))
        self.fieldnames = [field[0] for field in fields]
        self.fieldspecs = [tuple(field[1:]) for field in fields]

        self.numrec = numrec
        return self.fieldnames, self.fieldspecs

    def _read_records(self):
        records = self.records
        if records:
            return records

        f = self.f
        fields = self.fields
        numrec = self.numrec
        records = self.records

        if not (self.fieldnames or self.fieldspecs):
            self._read_header()
        
        terminator = self._read(f, 1)
        terminator=terminator.decode('utf-8')
        assert terminator == '\r'

        fields.insert(0, ('DeletionFlag', 'C', 1, 0))
        fmt = ''.join(['%ds' % fieldinfo[2] for fieldinfo in fields])
        fmtsiz = struct.calcsize(fmt)
        for i in range(numrec):
            recordb = struct.unpack(fmt, self._read(f, fmtsiz))
            if len(recordb) > len(self.fieldnames):
                recordb = recordb[1:]
            records.append(list(recordb))

        return records

    def _write_header(self, fieldnames, fieldspecs, records):
        f = self.f
        f.seek(0, os.SEEK_SET)

        ver = 3
        now = datetime.datetime.now()
        yr, mon, day = now.year - 1900, now.month, now.day
        numrec = len(records)
        numfields = len(fieldspecs)
        lenheader = numfields * 32 + 33
        lenrecord = sum(field[1] for field in fieldspecs) + 1
        hdr = struct.pack('<BBBBLHH20x', ver, yr, mon, day, numrec, lenheader, lenrecord)
        f.write(hdr)

        # field specs
        for name, (typ, size, deci) in zip(fieldnames, fieldspecs):
            name = name.ljust(11, '\x00')
            name = name.encode('utf-8')
            typ = typ.encode('utf-8')
            fld = struct.pack('<11sc4xBB14x', name, typ, size, deci)
            f.write(fld)

        # terminator
        f.write(b'\r\n')

    def _write_records(self):

        f = self.f
        fieldnames = self.fieldnames
        fieldspecs = self.fieldspecs
        records = self.records

        for record in records:
            for (typ, size, deci), value in zip(fieldspecs, record):
                if typ == "N":
                    value = str(value).rjust(size, ' ')
                    value = value.encode('utf-8')
                elif typ == 'D':
                    value = value.strftime('%Y%m%d')
                    value = value.encode('utf-8')
                elif typ == 'L':
                    value = str(value)[0].upper()
                    value = value.encode('utf-8')
                else:
                    value = str(value)[:size].ljust(size, ' ')

                    # support chinese encoding GBK
                    if len(value) != len(value.encode("GBK")):
                        value = value.encode("GBK")[:size]
                    else:
                        value = value.encode('utf-8')

                assert len(value) == size
                f.write(value)
            
            f.write(b' ')

        # End of file
        f.write(b'\x1A')

        # sign write_records
        self.write_records = copy.deepcopy(records)

    def lixx_read(self):
        return self._read_records()
    
    def lixx_write(self, fieldnames=None, fieldspecs=None, records=None):
        
        if not fieldnames:
            fieldnames = self.fieldnames
        else:
            self.fieldnames = fieldnames
        if not fieldspecs:
            fieldspecs = self.fieldspecs
        else:
            self.fieldspecs = fieldspecs
        if not records:
            records = self.records
        else:
            self.records = records

        self._write_header(fieldnames, fieldspecs, records)
        self._write_records()
    
    def lixx_get(self, row, col=None):
        if not self.records:
            self._read_records()

        return self.records[row][col]
    
    def lixx_set(self, row, col, val):
        records = self.records
        col_size = len(self.fieldnames)

        if col >= col_size:
            raise ValueError("Invalid col index.\nThe size of fieldnames is %d" % col_size)
        
        records[row][col] = val
        return records[row][col]
    
    def lixx_info(self):
        """header info, size, type, etc."""
        return "Path: %s\nFieldnames: %s\nFieldspecs: %s" % (self.path, self.fieldnames, self.fieldspecs)

if __name__ == '__main__':
    pass

