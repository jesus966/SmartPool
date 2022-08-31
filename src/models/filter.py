import datetime
import logging

import src.config.configconstants as cfg
import src.strings_constants.strings as strings
from src.database.models import FilterData
from src.sensors import diatomsPressureSensor, sandPressureSensor

from pymongo import errors

class Filter:
    """
    This class represents a filter of the pool.
    """

    '''
    Filter's attributes
    '''
    type = None
    pressure = None
    is_ok = False

    def __init__(self, filter_type):
        """
        Constructor of the class
        """

        # Store what type of filter is
        self.type = filter_type
        if filter_type == cfg.DIATOMS_TYPE:
            diatomsPressureSensor.add_callback(self.__add_diatoms_pressure__)
        elif filter_type == cfg.SAND_TYPE:
            sandPressureSensor.add_callback(self.__add_sand_pressure__)
        logging.log(logging.DEBUG, strings.LOG_FILTER_INSTANTIATED, filter_type)

    def __add_diatoms_pressure__(self, *args):
        """
        This method adds a new pressure value
        """
        if diatomsPressureSensor.is_ok:
            self.pressure = diatomsPressureSensor.value

    def __add_sand_pressure__(self):
        """
        This method adds a new pressure value
        """
        if sandPressureSensor.is_ok:
            self.pressure = sandPressureSensor.value

    def save_to_db(self):
        """
        This method saves the current filter into the database
        """
        try:
            # Create a new SensorData object in database and save all the data
            filterdb = FilterData()
            filterdb.type = self.type
            filterdb.pressure = self.pressure
            filterdb.datetime = datetime.datetime.utcnow()
            filterdb.save()
        except errors.PyMongoError:
            pass
