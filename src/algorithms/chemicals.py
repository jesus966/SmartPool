import datetime
import logging

import numpy as np
import pymongo

from pymongo import errors

import src.strings_constants.strings as strings
from src.database import timezone
from src.database.db import db
from src.database.models import ChemicalsAlgorithmData
from src.models import Timer, actuators, water
import src.config.configconstants as cfg
from src.config.pool import poolcfg
from bson.codec_options import CodecOptions


class Chemicals:
    """
    This is a class that implements the pool Chemical control Algorithm
    """

    orp_setpoint = poolcfg.pool_orp_mv_setpoint
    ph_setpoint = poolcfg.pool_ph_setpoint
    algorithm_cycle_seconds = 15 * 60
    algorithm_orp_injected_seconds = 0
    algorithm_ph_injected_seconds = 0
    ph_auto_injection_disabled = poolcfg.pool_ph_auto_injection_disabled
    orp_auto_injection_disabled = poolcfg.pool_orp_auto_injection_disabled
    max_orp_daily_seconds = poolcfg.pool_max_orp_daily_seconds
    max_ph_daily_seconds = poolcfg.pool_max_ph_daily_seconds
    total_orp_daily_seconds = 0
    total_ph_daily_seconds = 0
    main_timer = None
    day = datetime.datetime.now().day

    def __init__(self):
        logging.log(logging.INFO, strings.LOG_CHEMICALS_INSTANTIATED)
        self.load_from_db()

        # Map poolcfg variables to the update method
        poolcfg.pool_ph_setpoint_cb = self._update_config
        poolcfg.pool_orp_mv_setpoint_cb = self._update_config
        poolcfg.pool_ph_auto_injection_disabled_cb = self._update_config
        poolcfg.pool_orp_auto_injection_disabled_cb = self._update_config
        poolcfg.pool_max_orp_daily_seconds_cb = self._update_config
        poolcfg.pool_max_ph_daily_seconds_cb = self._update_config

        # Start algorithm cycle timer
        main_timer = Timer(self._cycle)
        main_timer.start()

    def _update_config(self):
        """
        This method is called when the pool cfg has been changed to update
        changes in this class.
        """
        self.ph_auto_injection_disabled = poolcfg.pool_ph_auto_injection_disabled
        self.orp_auto_injection_disabled = poolcfg.pool_orp_auto_injection_disabled
        self.max_orp_daily_seconds = poolcfg.pool_max_orp_daily_seconds
        self.max_ph_daily_seconds = poolcfg.pool_max_ph_daily_seconds
        self.orp_setpoint = poolcfg.pool_orp_mv_setpoint
        self.ph_setpoint = poolcfg.pool_ph_setpoint

    def _cycle(self):
        """
        This method is called every second and its has the chemical injection
        algorithm
        """

        # First, this algorithm only works when not in emergency mode, when the filter
        # pump is ON and in automatic mode, and when the water sensor data is valid.
        if not actuators.IN_EMERGENCY_STOP and actuators.FILTER_PUMP_REAL_STATE \
                and actuators.PUMP_AUTOMATIC_CONTROL and water.valid:

            # In this case, we are ready to execute the chemical injection algorithm

            # If a cycle of 15 minutes has passed, recalculate a new cycle of injections
            if self.algorithm_cycle_seconds >= 15 * 60:
                if water.orp is not None:
                    if not self.orp_auto_injection_disabled and water.orp < self.orp_setpoint:
                        # ORP levels are below the setpoint, calculate total injection seconds
                        error = self.orp_setpoint - water.orp

                        # It's a P type control algorithm
                        if error > 150:
                            self.algorithm_orp_injected_seconds = 14 * 60
                        elif 150 >= error >= 25:
                            self.algorithm_orp_injected_seconds = int(np.round(5.28 * error - 72))
                        else:
                            self.algorithm_orp_injected_seconds = 60

                        logging.log(logging.INFO, strings.LOG_CHEMICALS_ORP_ERROR, error,
                                    self.algorithm_orp_injected_seconds)
                    else:
                        if not self.orp_auto_injection_disabled:
                            logging.log(logging.INFO, strings.LOG_CHEMICALS_NO_ORP_ERROR)
                        self.algorithm_orp_injected_seconds = 0

                if water.ph is not None:
                    if not self.ph_auto_injection_disabled and water.ph > self.ph_setpoint:
                        # PH levels are below the setpoint, calculate total injection seconds
                        error = water.ph - self.ph_setpoint

                        # It's a P type control algorithm
                        if error > 0.4:
                            self.algorithm_ph_injected_seconds = 14 * 60
                        else:
                            self.algorithm_ph_injected_seconds = int(np.round(1800 * error))

                        logging.log(logging.INFO, strings.LOG_CHEMICALS_PH_ERROR, error,
                                    self.algorithm_ph_injected_seconds)
                    else:
                        if not self.ph_auto_injection_disabled:
                            logging.log(logging.INFO, strings.LOG_CHEMICALS_NO_PH_ERROR)
                        self.algorithm_ph_injected_seconds = 0

                self.algorithm_cycle_seconds = -1
            else:
                # We are on an injection cycle, assure that we are injecting and check statistics

                # Check if the algorithm has been disabled, and disable pumps if yes.
                if self.orp_auto_injection_disabled or self.total_orp_daily_seconds > self.max_orp_daily_seconds:
                    self.algorithm_orp_injected_seconds = 0

                if self.ph_auto_injection_disabled or self.total_ph_daily_seconds > self.max_ph_daily_seconds:
                    self.algorithm_ph_injected_seconds = 0

                # If there are seconds remaining and the pump is not ON, turn it on
                # or if we have finished and the pump is ON, turn it off
                if self.algorithm_orp_injected_seconds > 0 and not actuators.BLEACH_PUMP_STATE:
                    actuators.setstate(cfg.BLEACH_PUMP, True)

                if self.algorithm_ph_injected_seconds > 0 and not actuators.ACID_PUMP_STATE:
                    actuators.setstate(cfg.ACID_PUMP, True)

                if self.algorithm_orp_injected_seconds <= 0 and actuators.BLEACH_PUMP_STATE:
                    actuators.setstate(cfg.BLEACH_PUMP, False)

                if self.algorithm_ph_injected_seconds <= 0 and actuators.ACID_PUMP_STATE:
                    actuators.setstate(cfg.ACID_PUMP, False)

                # If the pumps are running, decrease seconds countdown.

                if actuators.BLEACH_PUMP_STATE:
                    self.algorithm_orp_injected_seconds -= 1
                    self.total_orp_daily_seconds += 1

                if actuators.ACID_PUMP_STATE:
                    self.algorithm_ph_injected_seconds -= 1
                    self.total_ph_daily_seconds += 1

            # Increase algorithm execution cycle seconds
            self.algorithm_cycle_seconds += 1
            self.save_to_db()

        else:
            # If this is not the case, check that we are not in emergency stop, and we are on automatic
            # to check if the chemical pumps are on and needs to be stopped.
            if not actuators.IN_EMERGENCY_STOP and actuators.PUMP_AUTOMATIC_CONTROL and \
                    (actuators.BLEACH_PUMP_STATE or actuators.ACID_PUMP_STATE):
                # Stop chemical pumps
                actuators.setstate(cfg.BLEACH_PUMP, False)
                actuators.setstate(cfg.ACID_PUMP, False)

        if datetime.datetime.now().day != self.day:
            # Day has changed, reset statistics
            self.day = datetime.datetime.now().day
            self.total_ph_daily_seconds = 0
            self.total_orp_daily_seconds = 0

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("chemicals_algorithm_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]
            self.algorithm_cycle_seconds = record["algorithm_cycle_seconds"]
            self.algorithm_orp_injected_seconds = record["algorithm_orp_injected_seconds"]
            self.algorithm_ph_injected_seconds = record["algorithm_ph_injected_seconds"]
            if self.day != record["datetime"].day:
                self.total_orp_daily_seconds = 0
                self.total_ph_daily_seconds = 0
            else:
                self.total_orp_daily_seconds = record["total_orp_daily_seconds"]
                self.total_ph_daily_seconds = record["total_ph_daily_seconds"]
            logging.log(logging.INFO, strings.LOG_CHEMICALS_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_CHEMICALS_NOT_LOADED)

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            col = db.get_db().get_collection("chemicals_algorithm_data").with_options(
                    codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))

            # Create a new object in database and save all the data
            chemicalsdb = ChemicalsAlgorithmData()

            chemicalsdb.datetime = timezone.localize(datetime.datetime.now())
            chemicalsdb.algorithm_cycle_seconds = self.algorithm_cycle_seconds
            chemicalsdb.algorithm_orp_injected_seconds = self.algorithm_orp_injected_seconds
            chemicalsdb.algorithm_ph_injected_seconds = self.algorithm_ph_injected_seconds
            chemicalsdb.total_orp_daily_seconds = self.total_orp_daily_seconds
            chemicalsdb.total_ph_daily_seconds = self.total_ph_daily_seconds
            col.replace_one({}, chemicalsdb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass
