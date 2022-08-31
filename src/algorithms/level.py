import datetime
import logging
import time

import pymongo
from bson.codec_options import CodecOptions

import src.strings_constants.strings as strings
from src.config.pool import poolcfg
from src.database import timezone
from src.database.db import db
from src.database.models import LevelAlgorithmData
from src.models import Timer, actuators, water
import src.config.configconstants as cfg
from src.sensors.subtypes import flowSensor

from pymongo import errors

class Level:
    """
    This is a class that implements the pool water level control Algorithm
    """

    fill_level_timer = None

    state = cfg.STATE_WAITING_FOR_FILL
    daily_filled_volume = 0
    start_volume = 0

    day = datetime.datetime.now().day

    def __init__(self):
        logging.log(logging.INFO, strings.LOG_LEVELS_INSTANTIATED)
        self.load_from_db()
        self.fill_level_timer = Timer(self._level_control, period=1)
        self.fill_level_timer.start()

    def _level_control(self):
        """
        This timer executes every second the fill level control algorithm
        """
        if self.state == cfg.STATE_WAITING_FOR_FILL:
            # Check that we are on automatic fill control
            if actuators.VALVE_AUTOMATIC_CONTROL:
                # Assure that fill valve is off
                if actuators.FILL_VALVE_STATE:
                    actuators.setstate(cfg.FILL_VALVE, False)

                # Check if there is no water in the fill start level
                no_water = not water.levels[poolcfg.pool_fill_start_level]

                # If there is no water, change state
                if no_water is not None and no_water \
                        and self.daily_filled_volume < poolcfg.pool_max_daily_water_volume_m3:
                    # Turn on Fill valve and change state
                    self.start_volume = flowSensor.daily_volume
                    self.state = cfg.STATE_FILLING
                    actuators.setstate(cfg.FILL_VALVE, True)
                    logging.log(logging.INFO, strings.LOG_LEVELS_STATE, cfg.STATE_FILLING)

        elif self.state == cfg.STATE_FILLING:
            # Check if we are on automatic control
            if actuators.VALVE_AUTOMATIC_CONTROL:
                # Check that the fill valve is ON
                if not actuators.FILL_VALVE_STATE:
                    actuators.setstate(cfg.FILL_VALVE, True)

                # Check if we have reached the target volume
                difference = flowSensor.daily_volume - self.start_volume

                # If there has been a day change, set new start volume
                if difference < 0:
                    self.start_volume = flowSensor.daily_volume
                    difference = 0

                # Update statistics
                self.daily_filled_volume += difference

                # Check that we have not reached the max daily filter volume
                if self.daily_filled_volume <= poolcfg.pool_max_daily_water_volume_m3:

                    if difference >= poolcfg.pool_fill_volume_between_checks:
                        # Stop fill valve
                        actuators.setstate(cfg.FILL_VALVE, False)

                        # Wait a given amount of time
                        time.sleep(poolcfg.pool_fill_seconds_wait)

                        # Check if we have reached the desired water level
                        reached = water.levels[poolcfg.pool_fill_end_level]

                        # If yes, change state if no, continue filling
                        if reached is not None and reached:
                            self.state = cfg.STATE_WAITING_FOR_FILL
                            logging.log(logging.INFO, strings.LOG_LEVELS_STATE, cfg.STATE_WAITING_FOR_FILL)
                        else:
                            self.start_volume = flowSensor.daily_volume
                            actuators.setstate(cfg.FILL_VALVE, True)
                else:
                    # Stop fill valve and change state
                    actuators.setstate(cfg.FILL_VALVE, False)
                    self.state = cfg.STATE_WAITING_FOR_FILL
                    logging.log(logging.INFO, strings.LOG_LEVELS_STATE, cfg.STATE_WAITING_FOR_FILL)

        if datetime.datetime.now().day != self.day:
            # Day has changed, reset statistics
            self.day = datetime.datetime.now().day
            self.daily_filled_volume = 0

        self.save_to_db()

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("level_algorithm_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]

            if self.day != record["datetime"].day:
                self.daily_filled_volume = 0
            else:
                self.daily_filled_volume = record["daily_filled_volume"]

            logging.log(logging.INFO, strings.LOG_LEVELS_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_LEVELS_NOT_LOADED)

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            col = db.get_db().get_collection("level_algorithm_data").with_options(
                    codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))

            # Create a new object in database and save all the data
            leveldb = LevelAlgorithmData()

            leveldb.datetime = timezone.localize(datetime.datetime.now())
            leveldb.state = self.state
            leveldb.daily_filled_volume = self.daily_filled_volume
            leveldb.start_volume = self.start_volume

            # If there is a new day save a new record, if not update last record
            if self.day != datetime.datetime.now().day:
                leveldb.save()
            else:
                col.replace_one({}, leveldb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass
