class Switcher(object):
    def numbers_to_methods_to_strings(self, argument):
        """Dispatch method"""
        # prefix the method_name with 'number_' because method names
        # cannot begin with an integer.
        method_name = 'number_' + str(argument)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "nothing")
        # Call the method as we return it
        return method()

    def number_0(self):
        return "zero"

    def number_1(self):
        return "one"

    def number_2(self):
        return "two"
if __name__ == '__main__':
    Switcher=Switcher()
    print Switcher.numbers_to_methods_to_strings('0')