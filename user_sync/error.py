class AssertionException(Exception):
    def __init__(self, message):
        super(AssertionException, self).__init__(message)
        self.reported = False

    def set_reported(self):        
        self.reported = True

    def is_reported(self):
        return self.reported