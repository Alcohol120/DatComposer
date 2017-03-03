class Callback:

    def __init__(self):

        self.callback = object

        pass

    def assert_error(self, message, title=False):

        callback_method = getattr(self.callback, "assert_error", None)

        if callback_method is not None:
            if title:
                callback_method(message, title)
            else:
                callback_method(message)
        else:
            print(message)

        pass

    def assert_success(self, message, title=False):

        callback_method = getattr(self.callback, "assert_success", None)

        if callback_method is not None:
            if title:
                callback_method(message, title)
            else:
                callback_method(message)
        else:
            print(message)

        pass

    def set_callback(self, callback):

        self.callback = callback

        pass

    pass
