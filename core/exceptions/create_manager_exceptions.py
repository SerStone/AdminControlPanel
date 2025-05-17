class UsernameTooLongException(Exception):
    def __init__(self, max_length):
        self.max_length = max_length
        super().__init__(f"Username exceeds maximum length of {max_length} characters.")