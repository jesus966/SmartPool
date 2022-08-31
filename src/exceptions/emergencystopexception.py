class EmergencyStopException(Exception):
    """
    This exception is thrown when we try to actuate in a pump while in emergency stop mode.
    """
    def __init__(self, message="Attempted to manipulate a pump while in emergency stop."):
        super().__init__(message)

