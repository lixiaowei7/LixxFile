# <Lixx_file, a model for reading and writing uncommon files.>
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

class LixxFile():
    """a base class model for reading and writing uncommon files."""

    def __init__(self, path):
        pass

    def __del__(self):
        pass

    def __str__(self):
        return self.lixx_info()

    def lixx_read(self):
        pass
    
    def lixx_write(self):
        pass

    def lixx_get(self):
        pass
    
    def lixx_set(self):
        pass
    
    def lixx_info(self):
        """header info, size, type, etc."""
        pass

if __name__ == '__main__':
    pass