class Callback:

    def __init__(self):

        self.callback = object

        pass

    def assert_error(self, message, title=False):

        callback_method = getattr(self.callback, "assert_error", None)

        if callback_method is not None:
            callback_method(message, title)
        else:
            print(message)

        pass

    def set_callback(self, callback):

        self.callback = callback

        pass

    pass
