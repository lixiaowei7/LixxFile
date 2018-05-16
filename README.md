# LixxFile


### DBF_Write
    >>> dbf = LixxDBF('xx.dbf')
    >>> fieldnames = ['name', 'title']
    >>> fieldspecs = [('C', 16, 0), ('C', 16, 0)]
    >>> records = [["Xiaowei Li", "Archon"], ["Xixiang Zhu", "CAO"]]
    >>> dbf.lixx_write(fieldnames, fieldspecs, records)

### DBF_Read
    >>> dbf = LixxDBF('xx.dbf')
    >>> dbf.fieldnames
    ['name', 'title']
    >>> dbf.fieldspecs
    [('C', 16, 0), ('C', 16, 0)]
    >>> dbf.lixx_read()
    [[b'Xiaowei Li      ', b'Archon          '], [b'Xixiang Zhu     ', b'CAO             ']]
    >>> dbf.lixx_get(1, 1)
    b'CAO
    >>> dbf.lixx_set(0, 1, 'X')
    'X'
    >>> dbf
    Xiaowei Li, X
    Xixiang Zhu, CAO
    
    >>> repr(dbf)
    'Xiaowei Li, X\nXixiang Zhu, CAO\n'
    >>> print(dbf)
    Path: xx.dbf
    Fieldnames: ['name', 'title']
    Fieldspecs: [('C', 16, 0), ('C', 16, 0)]

### *License*
LixxFile is released under the [GPL license](https://www.gnu.org/licenses/).

    Copyright (C) <2018>  <Xiaowei Li, Xixiang Zhu>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    @Email: Xiaowei Li<lixiaowei7@live.cn>
    @Email: Xixiang Zhu<hixxzhu@gmail.com>
