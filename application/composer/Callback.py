class Callback:

    def __init__(self):

        self._callback = object

        pass

    def assert_error(self, message, title=False):

        callback_method = getattr(self._callback, "assert_error", None)

        if callback_method is not None:
            callback_method(message, title)

        pass

    def set_callback(self, callback):

        self._callback = callback

        pass

    pass
