from functools import wraps


def foo_decorator(f):
    @wraps(f)
    async def g(*args, **kwargs):
        print("Running decoration for function {}".format(f.__name__))
        return await f(*args, **kwargs)

    return g


def fun(f):
    def g(*args, **kwargs):
        return f(*args, **kwargs)

    return g


class Foo(object):
    @foo_decorator
    async def bar():
        print("Running function bar!")

    async def baz():
        print("Running function baz!")

    @fun
    def barbaz():
        print("running")


x = Foo()
print(x.bar)
print(x.baz)
print(x.barbaz)
