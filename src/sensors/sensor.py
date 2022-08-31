import datetime
import logging

import src.strings_constants.strings as strings
from src.database import timezone
from src.database.models import SensorData
from flask import jsonify

from pymongo import errors

class Sensor:
    """
    This class represents a base class for all the pool's sensors
    """

    '''
    Sensor's attributes
    '''
    sensor_type = None
    value = None
    is_ok = None
    datetime = None
    previous_value = None
    previous_is_ok = None
    previous_datetime = None

    '''
    Sensor max and min values to be considered OK
    '''
    max_value = None
    min_value = None

    '''
    Callback function to be called when the value changed
    '''
    callback_list_owner = []
    callback_list = []
    args_list = []
    kwargs_list = []

    def __init__(self, sensor_type, max_value=None, min_value=None, callback=None):
        """
        Constructor of the class
        """

        # Store what type of sensor is
        self.sensor_type = sensor_type
        self.add_callback(callback)
        self.max_value = max_value
        self.min_value = min_value
        logging.log(logging.DEBUG, strings.LOG_SENSOR_INSTANTIATED, sensor_type)

    def add_callback(self, callback, *args, **kwargs):
        """
        This functions adds a callback to be executed when the sensor value changes.

        Args:
            callback: Function to callback

        Returns: None

        """
        if callback is not None:
            self.callback_list_owner.append(self.sensor_type)
            self.callback_list.append(callback)
            self.args_list.append(args)
            self.kwargs_list.append(kwargs)

    def check_value(self, value):
        """
        This method check if the given value is a valid
        value for the sensor or not
        """
        self.is_ok = True

        if value is None:
            self.is_ok = False
        elif self.max_value is not None and value > self.max_value:
            self.is_ok = False
        elif self.min_value is not None and value < self.min_value:
            self.is_ok = False

    def add_value(self, value, save=True):
        """
        This method adds a new sensor value
        """

        # Store the new sensor data and save its previous value
        self.previous_value = self.value
        self.value = value

        # Check if the new value is ok
        self.previous_is_ok = self.is_ok
        self.check_value(value)
        if self.is_ok:
            logging.log(logging.DEBUG, strings.LOG_SENSOR_NEW_VALID_VALUE, self.sensor_type)
        else:
            logging.log(logging.DEBUG, strings.LOG_SENSOR_NEW_INVALID_VALUE, self.sensor_type)

        # Store the current datetime and its previous value
        self.previous_datetime = self.datetime
        self.datetime = timezone.localize(datetime.datetime.now())

        if save:
            # Save to database
            self.save_to_db()

        for i in range(len(self.callback_list)):
            if self.callback_list_owner[i] == self.sensor_type:
                self.callback_list[i](*self.args_list[i], **self.kwargs_list[i])

    def save_to_db(self):
        """
        This method saves the current sensor into the database
        """
        try:
            # Create a new SensorData object in database and save all the data
            sensordb = SensorData()
            sensordb.id_value = {self.sensor_type: self.value}
            sensordb.is_ok = self.is_ok
            sensordb.datetime = self.datetime
            sensordb.save()
        except errors.PyMongoError:
            pass

    def to_json(self):
        """
        This method converts all the info contained in the sensor to JSON
        """
        if self.datetime is not None:
            sensor_data = {"datetime": self.datetime, "sensor_data": self.value, "is_ok": self.is_ok}
        else:
            sensor_data = ""
        return jsonify(sensor_data)
