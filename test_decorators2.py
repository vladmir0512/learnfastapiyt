from functools import wraps


def decorator(func):
    @wraps(func)
    def wrapper(a):
        """Wrapper"""
        print(wrapper)
        try:
            func(a)
        except ZeroDivisionError as error:
            print(error)

        print(wrapper)
    return wrapper

@decorator
def hello_divider(a):
    """Hello divider"""
    print("hello")
    print(10/a)
#
# hello_divider = decorator(hello_divider)

hello_divider(0)
print(hello_divider.__doc__)
print(wraps.__doc__)