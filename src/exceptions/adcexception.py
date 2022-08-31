
class AdcException(Exception):
    """
    This exception is throw when an error was found receiving ADC data
    """
    def __init__(self, message="Error while receiving ADC data."):
        super().__init__(message)

