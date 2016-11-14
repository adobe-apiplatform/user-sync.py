class AssertionException(Exception):
    def __init__(self, message):
        super(AssertionException, self).__init__(message)
