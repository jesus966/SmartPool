import logging
import datetime

from pymongo import errors

import src.strings_constants.strings as strings
from src.database import timezone
from src.driver import driver
from src.database.models import ActuatorData


class Actuator:
    """
    This class represents an actuator
    """

    '''
    Actuator's attributes
    '''
    actuator_type = None
    state = False
    datetime = None
    previous_state = None
    previous_datetime = None

    def __init__(self, actuator_type):
        """
        Constructor of the class
        """

        # Store what type of actuator is
        self.actuator_type = actuator_type
        logging.log(logging.DEBUG, strings.LOG_ACTUATOR_INSTANTIATED, actuator_type)

    def setstate(self, state):
        """
        This method changes the current actuator state
        """
        # Call the driver to change the state
        driver.set_state(self.actuator_type, state)

        # Store the new sensor data and save its previous value
        self.previous_state = self.state
        self.state = state

        # Store the current datetime and its previous value
        self.previous_datetime = self.datetime
        self.datetime = timezone.localize(datetime.datetime.now())

        # Save to database
        self.save_to_db()

    def save_to_db(self):
        """
        This method saves the current sensor into the database
        """
        try:
            # Create a new SensorData object in database and save all the data
            actuator_db = ActuatorData()
            actuator_db.actuator_id = self.actuator_type
            actuator_db.state = self.state
            actuator_db.datetime = self.datetime
            actuator_db.save()
        except errors.PyMongoError:
            pass

