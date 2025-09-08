class QuantaCircError(Exception):
    def __init__(self, message, suggested_fix=None):
        self.message = message
        self.suggested_fix = suggested_fix
        super().__init__(self.message)
