class Decorator:

    def __init__(self, func):
        self.func = func

    def __call__(self, a):
        try:
            self.func(a)
        except ZeroDivisionError as error:
            print(error)
