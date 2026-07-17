def decorator(func):
    def wrapper(a):
        try:
           func(a)
        except ZeroDivisionError as error:
            print(error)
    return wrapper



def hello_divider(a: int):
    print("Hello")
    print(10 / a)

hello_divider = decorator(hello_divider)

hello_divider(0)