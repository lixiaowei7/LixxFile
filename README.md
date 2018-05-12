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
    >>> dbf._read_records()
    [[b'Xiaowei Li      ', b'Archon          '], [b'Xixiang Zhu     ', b'CAO             ']]
    >>> dbf
    Fieldnames: ['name', 'title']
    Fieldspecs: [('C', 16, 0), ('C', 16, 0)]
    >>> print(repr(dbf))
    Xiaowei Li, Archon
    Xixiang Zhu, CAO

