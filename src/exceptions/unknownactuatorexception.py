
class UnknownActuatorException(Exception):
    """
    This exception is throw when we try to set a new state for an actuator that doesn't exist
    """
    def __init__(self, message="Actuator not found."):
        super().__init__(message)

