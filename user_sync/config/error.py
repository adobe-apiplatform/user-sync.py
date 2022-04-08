from user_sync.error import AssertionException


class ConfigValidationError(AssertionException):
    def __init__(self, message):
        super(ConfigValidationError, self).__init__(message)
