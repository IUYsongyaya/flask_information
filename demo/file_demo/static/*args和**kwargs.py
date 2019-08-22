def test2(a, b, *args, **kwargs):
    print(a)
    print(b)
    print(args)
    print(kwargs)



def test1(a, b, *args, **kwargs):
    # print(a)
    # print(b)
    # test2(a, b, args[:], kwargs[:])
    # print(args[:])
    # print(kwargs[:])
    pass

test1(1, 2, 3, 4, name='zxc', age='12')
