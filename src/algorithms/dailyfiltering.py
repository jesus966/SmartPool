import datetime
import logging

import numpy as np
import pymongo

import src.config.configconstants as cfg
import src.strings_constants.strings as strings
from src.config.pool import poolcfg
from src.database import timezone
from src.database.db import db
from src.database.models import FilterAlgorithmData
from src.models import actuators, water, Timer
from bson.codec_options import CodecOptions

from pymongo import errors

class DailyFiltering:
    """
    This is a class that implements the pool daily filtering control Algorithm
    """

    '''
    Daily filtering variables
    '''
    state = cfg.STATE_WAITING_DAILY_CYCLE
    allowed_hours = poolcfg.daily_filter_allowed_hours
    total_daily_seconds = 0
    total_daily_seconds_remaining = 0
    day = datetime.datetime.now().day
    filtering_timer = None

    def __init__(self):
        logging.log(logging.DEBUG, strings.LOG_DFILT_INSTANTIATED)
        self.load_from_db()
        poolcfg.daily_filter_allowed_hours_cb = self._update_config
        water.add_cb(self.__update__)
        self.filtering_timer = Timer(self.__filter__)
        self.filtering_timer.start()

    def _update_config(self):
        """
        This method updates current config from poolcfg.
        """
        self.allowed_hours = poolcfg.daily_filter_allowed_hours

    def __update__(self):
        """
        This method is called everytime there is a temperature change, and it calculates the new
        total max daily seconds value.
        """
        # Get current water temperature
        temp = water.temperature

        if temp is not None:

            # Change K-factor depending on the temperature
            if temp > 15:
                K = 1
            elif 15 >= temp >= 13:
                K = 0.5
            elif 12 >= temp >= 10:
                K = 1 / 3
            elif 9 >= temp >= 6:
                K = 0.25
            else:
                K = 0.15

            # Calculate the total daily filtering seconds
            total_seconds = np.ceil(K * ((temp / poolcfg.pool_hydrodynamic_factor)
                                         * poolcfg.pool_recirculation_period) * 60 * 60)

            # Get the variation between las max total daily seconds and the new max
            delta = total_seconds - self.total_daily_seconds
            self.total_daily_seconds = total_seconds

            # Add this delta to the total daily seconds remaining
            self.total_daily_seconds_remaining += delta

            self.save_to_db()

    def __filter__(self):
        """
        This method is called every second, and it updates filtering statistics
        and as well turn ON/OFF filtering.

        Returns:

        """
        # Check in what state we are
        if self.state == cfg.STATE_WAITING_DAILY_CYCLE:
            # Check if we are on an allowed hours and there are seconds pending
            if self.total_daily_seconds_remaining > 0:
                if datetime.datetime.now().hour in self.allowed_hours:
                    '''
                        There are remaining daily filter seconds, and we are on an allowed hour
                        check that we aren't on manual or emergency stop mode, and turn on the filter
                    '''
                    if not actuators.IN_EMERGENCY_STOP and actuators.PUMP_AUTOMATIC_CONTROL:
                        # Change state
                        actuators.setstate(cfg.FILTER_PUMP, True)
                        self.state = cfg.STATE_FILTERING
                        logging.log(logging.INFO, strings.LOG_DFILT_STATE_CHANGE, cfg.STATE_FILTERING)
                        self.save_to_db()
            elif not actuators.IN_EMERGENCY_STOP and actuators.PUMP_AUTOMATIC_CONTROL \
                    and actuators.FILTER_PUMP_TEORIC_STATE:
                actuators.setstate(cfg.FILTER_PUMP, False)

        elif self.state == cfg.STATE_FILTERING:
            # Update statistics

            if self.total_daily_seconds_remaining > 0 and datetime.datetime.now().hour in self.allowed_hours:
                if actuators.PUMP_AUTOMATIC_CONTROL:
                    if actuators.FILTER_PUMP_REAL_STATE:
                        self.total_daily_seconds_remaining -= 1
                        self.save_to_db()
            else:
                # Change state
                actuators.setstate(cfg.FILTER_PUMP, False)
                self.state = cfg.STATE_WAITING_DAILY_CYCLE
                logging.log(logging.INFO, strings.LOG_DFILT_STATE_CHANGE, cfg.STATE_WAITING_DAILY_CYCLE)
                self.save_to_db()

        # Check if this is another day
        if self.day != datetime.datetime.now().day:
            # Reset counters
            self.day = datetime.datetime.now().day
            self.total_daily_seconds_remaining = self.total_daily_seconds

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("filter_algorithm_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]

            if self.day != record["datetime"].day:
                self.total_daily_seconds = 0
                self.total_daily_seconds_remaining = 0
            else:
                self.total_daily_seconds = record["total_daily_seconds"]
                self.total_daily_seconds_remaining = record["total_daily_seconds_remaining"]

            logging.log(logging.INFO, strings.LOG_DFILT_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_DFILT_NOT_LOADED)

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            col = db.get_db().get_collection("filter_algorithm_data").with_options(
                    codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))

            # Create a new SensorData object in database and save all the data
            filterdb = FilterAlgorithmData()

            filterdb.datetime = timezone.localize(datetime.datetime.now())
            filterdb.total_daily_seconds = self.total_daily_seconds
            filterdb.total_daily_seconds_remaining = self.total_daily_seconds_remaining

            col.replace_one({}, filterdb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass

