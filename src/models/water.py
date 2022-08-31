import datetime
import logging

import numpy as np
import pymongo

import src.strings_constants.strings as strings
from src.config.pool import poolcfg
from src.database.db import db
from src.database.models import WaterData
from src.models import actuators, Timer
from src.sensors import temperatureSensor, orpSensor, phSensor, tdsSensor, waterLevelSensor_1, \
    waterLevelSensor_6, waterLevelSensor_5, waterLevelSensor_4, waterLevelSensor_3, waterLevelSensor_2
from src.database import timezone
from bson.codec_options import CodecOptions

from pymongo import errors

class Water:
    """
    This is a class that represents water in the pool.
    """
    temperature = None
    orp = None
    ph = None
    tds = None
    alkalinity = None
    hardness = None
    LSI = None
    cya = None
    levels = [False, False, False, False, False, False]
    valid = False

    '''
    Vectors for the sensors
    '''
    temperature_vector = []
    orp_vector = []
    ph_vector = []
    tds_vector = []

    '''
    Variables for storing timers
    '''
    data_refresh_timer = None

    '''
    Callback function to be called when the value changed
    '''
    callback_list = []

    def __init__(self):
        logging.log(logging.INFO, strings.LOG_WATER_INSTANTIATED)
        # Set sensor callbacks
        temperatureSensor.add_callback(self.__add_temperature__)
        orpSensor.add_callback(self.__add_orp__)
        phSensor.add_callback(self.__add_ph__)
        tdsSensor.add_callback(self.__add_tds__)
        waterLevelSensor_1.add_callback(self.__add_level_1__)
        waterLevelSensor_2.add_callback(self.__add_level_2__)
        waterLevelSensor_3.add_callback(self.__add_level_3__)
        waterLevelSensor_4.add_callback(self.__add_level_4__)
        waterLevelSensor_5.add_callback(self.__add_level_5__)
        waterLevelSensor_6.add_callback(self.__add_level_6__)

        # Get current sensor values
        self.levels[0] = waterLevelSensor_1.value
        self.levels[1] = waterLevelSensor_2.value
        self.levels[2] = waterLevelSensor_3.value
        self.levels[3] = waterLevelSensor_4.value
        self.levels[4] = waterLevelSensor_5.value
        self.levels[5] = waterLevelSensor_6.value

        # Start timer
        self.data_refresh_timer = Timer(self.__update_data__, period=poolcfg.sensor_refresh_minutes * 60)
        self.data_refresh_timer.start()
        poolcfg.sensor_refresh_minutes_cb = self.__update_sensor_timer__

        # Load data
        self.load_from_db()

    def __add_level_1__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[0] = waterLevelSensor_1.value
        self.save_to_db()

    def __add_level_2__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[1] = waterLevelSensor_2.value
        self.save_to_db()

    def __add_level_3__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[2] = waterLevelSensor_3.value
        self.save_to_db()

    def __add_level_4__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[3] = waterLevelSensor_4.value
        self.save_to_db()

    def __add_level_5__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[4] = waterLevelSensor_5.value
        self.save_to_db()

    def __add_level_6__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        self.levels[5] = waterLevelSensor_6.value
        self.save_to_db()

    def __add_temperature__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        if temperatureSensor.is_ok:
            self.temperature_vector.append(temperatureSensor.value)

    def __add_orp__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        if orpSensor.is_ok:
            self.orp_vector.append(orpSensor.value)

    def __add_ph__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        if phSensor.is_ok:
            self.ph_vector.append(phSensor.value)

    def __add_tds__(self):
        """
        This method adds a new value into the vectors.
        Returns:

        """
        if tdsSensor.is_ok:
            self.tds_vector.append(tdsSensor.value)

    def __update_data__(self):
        """
        This is called periodically to update sensor data.

        Returns:

        """
        # Calculate mean of the data
        if not self.temperature_vector:
            self.temperature = None
        else:
            self.temperature = np.mean(self.temperature_vector)

        if not self.orp_vector:
            self.orp = None
        else:
            self.orp = np.mean(self.orp_vector)

        if not self.ph_vector:
            self.ph = None
        else:
            self.ph = np.mean(self.ph_vector)

        if not self.tds_vector:
            self.tds = None
        else:
            self.tds = np.mean(self.tds_vector)

        # Reset's vectors
        self.temperature_vector = []
        self.orp_vector = []
        self.ph_vector = []
        self.tds_vector = []

        # Check if the data is valid
        self.valid = False
        if actuators.FILTER_PUMP_SEC_SINCE_LAST_ON >= poolcfg.sensor_refresh_minutes * 60:
            self.valid = True

        # Save data
        self.save_to_db()

        # Execute callbacks
        for cb in self.callback_list:
            cb()

    def add_cb(self, callback):
        """
        This functions adds a callback to be executed when any water value changes.

        Args:
            callback: Function to callback

        Returns: None

        """
        if callback is not None:
            self.callback_list.append(callback)

    def __update_sensor_timer__(self):
        """
        This private function is called everytime the config changes
        and sets a new value for the sensor refresh timer.

        Returns:

        """
        self.data_refresh_timer.cancel()
        self.data_refresh_timer = Timer(self.__update_data__, period=poolcfg.sensor_refresh_minutes * 60)
        self.data_refresh_timer.start()

    def load_from_db(self):
        """
        This method search's for the lastest record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("water_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]
            try:
                self.alkalinity = record["alkalinity"]
            except KeyError:
                pass

            try:
                self.hardness = record["hardness"]
            except KeyError:
                pass

            try:
                self.LSI = record["LSI"]
            except KeyError:
                pass

            try:
                self.cya = record["cya"]
            except KeyError:
                pass

            logging.log(logging.INFO, strings.LOG_WATER_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_WATER_NOT_LOADED)

    def _update_LSI(self):
        """
        This method is called to update current LSI value
        """
        if self.cya is None:
            cya = 0
        else:
            cya = self.cya

        if self.tds is not None and self.temperature is not None and self.ph is not None \
                and self.alkalinity is not None and self.hardness is not None:

            log_tds = 11.13 + (1/3) * np.log10(self.tds)
            temp = 1.8 * self.temperature + 32
            log_temp = -(1/2000000)*np.power(temp, 3) + (3/50000)*np.power(temp, 2) + 0.0117*temp - 0.4116

            if 7.55 < self.ph:
                factor = 0.32 + 0.1*(self.ph-7.5)
            elif 7.85 < self.ph:
                factor = 0.35 + 0.05*(self.ph-7.8)
            else:
                factor = 0.12 + 0.2*(self.ph-6.5)

            carbonate_alkalinity = self.alkalinity - factor*cya
            log_ta = np.log10(carbonate_alkalinity)
            log_hardness = np.log10(self.hardness) - 0.4
            self.LSI = self.ph + log_temp + log_hardness + log_ta - log_tds
        else:
            self.LSI = None

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            # Create a new object in database and save all the data
            waterdb = WaterData()
            waterdb.datetime = timezone.localize(datetime.datetime.now())

            # Update current LSI
            self._update_LSI()

            if self.temperature is not None:
                waterdb.temperature = self.temperature
            if self.orp is not None:
                waterdb.orp = self.orp
            if self.ph is not None:
                waterdb.ph = self.ph
            if self.tds is not None:
                waterdb.tds = self.tds
            if self.alkalinity is not None:
                waterdb.alkalinity = self.alkalinity
            if self.hardness is not None:
                waterdb.hardness = self.hardness
            if self.LSI is not None:
                waterdb.LSI = self.LSI
            if self.cya is not None:
                waterdb.cya = self.cya

            level_array = {"water_level": self.levels}
            waterdb.levels = level_array
            waterdb.valid = self.valid
            waterdb.save()
        except errors.PyMongoError:
            pass
