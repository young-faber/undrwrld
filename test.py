def foo(a, *args, b=6, **kwargs): 
    print(a)
    print(args)
    print(b)
    print(kwargs)

foo(1, 2, 3, c=5, d=7)