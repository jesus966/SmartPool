
class BoardInitException(Exception):
    """
    This exception is throw when an error was found initializing the pool board
    """
    def __init__(self, message="Error while initiating board"):
        super().__init__(message)

