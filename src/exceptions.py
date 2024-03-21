SUPPRESS_TRACEBACK = True

class PandaCompilerError(Exception):
    """Base class for other panda compiler exceptions"""
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

    @staticmethod
    def exit_program():
        print("Exiting program due to critical error.")
        exit(1)

    def raise_err(self, exit=True):
        if SUPPRESS_TRACEBACK: 
            print(f"{self.__class__.__name__}: {self.message}")
            if exit: self.exit_program()
        else:
            raise self

#
# Tokenization Errors
#

class TokenizationError(PandaCompilerError):
    """Base class for tokenization exceptions"""
    pass

class UnrecognizedTokenError(TokenizationError):
    """Exception raised when an unrecognized token is encountered."""
    def __init__(self, token=None, message="Unrecognized token encountered"):
        self.token = token
        self.message = message
        super().__init__(self.message)