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
    Path: E:/GPL/xx.dbf
    Fieldnames: ['name', 'title']
    Fieldspecs: [('C', 16, 0), ('C', 16, 0)]
