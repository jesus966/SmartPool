
class ManualModeException(Exception):
    """
    This exception is thrown when we try to change the state of an actuator automatically, when
    we are on manual control.
    """
    def __init__(self, message="Tried to change the state when manual control is active."):
        super().__init__(message)

