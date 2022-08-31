import datetime
import logging

import pymongo

import src.strings_constants.strings as strings
from src.database.models import PoolConfigData
from src.database.db import db
import src.config.configconstants as cfg

from pymongo import errors

class PoolConfig:
    """
    This class hold ALL possible config constants of the pool. Its mission is to provide a wrapper that allow
    instant changes into the pool's configuration, and to provide support for loading and saving this info into
    the database.
    """

    '''
    Config variables related to the pool config
    '''
    sensor_refresh_minutes = cfg.SENSOR_REFRESH_MINUTES
    sensor_refresh_minutes_cb = None

    daily_filter_allowed_hours = cfg.DAILY_FILTER_ALLOWED_HOURS
    daily_filter_allowed_hours_cb = None

    pool_hydrodynamic_factor = cfg.POOL_HYDRODYNAMIC_FACTOR
    pool_recirculation_period = cfg.POOL_RECIRCULATION_PERIOD

    pool_orp_mv_setpoint = cfg.POOL_ORP_MV_SETPOINT
    pool_orp_mv_setpoint_cb = None
    pool_ph_setpoint = cfg.POOL_PH_SETPOINT
    pool_ph_setpoint_cb = None

    pool_orp_auto_injection_disabled = cfg.POOL_ORP_AUTO_INJECTION_DISABLED
    pool_orp_auto_injection_disabled_cb = None
    pool_ph_auto_injection_disabled = cfg.POOL_PH_AUTO_INJECTION_DISABLED
    pool_ph_auto_injection_disabled_cb = None

    pool_max_orp_daily_seconds = cfg.POOL_MAX_ORP_DAILY_SECONDS
    pool_max_orp_daily_seconds_cb = None
    pool_max_ph_daily_seconds = cfg.POOL_MAX_PH_DAILY_SECONDS
    pool_max_ph_daily_seconds_cb = None

    pool_flow_k_factor = cfg.POOL_FLOW_K_FACTOR
    pool_flow_k_factor_cb = None

    pool_fill_start_level = cfg.POOL_FILL_START_LEVEL
    pool_fill_end_level = cfg.POOL_FILL_END_LEVEL

    pool_max_daily_water_volume_m3 = cfg.POOL_MAX_DAILY_WATER_VOLUME_M3
    pool_fill_volume_between_checks = cfg.POOL_FILL_VOLUME_BETWEEN_CHECKS
    pool_fill_seconds_wait = cfg.POOL_FILL_SECONDS_WAIT

    pool_auto_lights_on = cfg.POOL_AUTO_LIGHTS_ON
    pool_auto_lights_on_command_sequence = {"sequence": cfg.POOL_AUTO_LIGHTS_ON_COMMAND_SEQUENCE}

    def __init__(self):
        logging.log(logging.INFO, strings.LOG_CFG_INSTANTIATED)
        self.load_from_db()

    def set_pool_auto_lights_on_command_sequence(self, sequence: list):
        """
        Sets the pool auto lights on command sequence

        Args:
            sequence: light sequence to be executed

        Returns:

        """
        self.pool_auto_lights_on_command_sequence = {"sequence": sequence}

        self.save_to_db()

    def set_pool_auto_lights_on(self, state: bool):
        """
        Sets the pool auto lights on

        Args:
            state: state disabled or enabled

        Returns:

        """
        self.pool_auto_lights_on = state

        self.save_to_db()

    def set_pool_fill_seconds_wait(self, seconds: int):
        """
        Sets the pool fill seconds wait

        Args:
            seconds: max seconds

        Returns:

        """
        self.pool_fill_seconds_wait = seconds

        self.save_to_db()

    def set_pool_fill_volume_between_checks(self, volume: float):
        """
        Sets the pool fill volume between checks

        Args:
            volume: volume in m3

        Returns:

        """
        self.pool_fill_volume_between_checks = volume

        self.save_to_db()

    def set_pool_max_daily_water_volume_m3(self, volume: float):
        """
        Sets the pool max daily water refill volume

        Args:
            volume: volume in m3

        Returns:

        """
        self.pool_max_daily_water_volume_m3 = volume

        self.save_to_db()

    def set_pool_fill_end_level(self, level: int):
        """
        Sets the pool fill end level

        Args:
            level: fill level

        Returns:

        """
        self.pool_fill_end_level = level

        self.save_to_db()

    def set_pool_fill_start_level(self, level: int):
        """
        Sets the pool fill start level

        Args:
            level: fill level

        Returns:

        """
        self.pool_fill_start_level = level

        self.save_to_db()

    def set_pool_flow_k_factor(self, factor: float):
        """
        Sets the pool flow k factor

        Args:
            factor: k factor

        Returns:

        """
        self.pool_flow_k_factor = factor
        self.save_to_db()
        if self.pool_flow_k_factor_cb is not None:
            self.pool_flow_k_factor_cb()

    def set_pool_max_ph_daily_seconds(self, seconds: int):
        """
        Sets the pool max ph daily seconds
        Args:
            seconds: max seconds

        Returns:

        """
        self.pool_max_ph_daily_seconds = seconds
        self.save_to_db()
        if self.pool_max_ph_daily_seconds_cb is not None:
            self.pool_max_ph_daily_seconds_cb()

    def set_pool_max_orp_daily_seconds(self, seconds: int):
        """
        Sets the pool max orp daily seconds
        Args:
            seconds: max seconds

        Returns:

        """
        self.pool_max_orp_daily_seconds = seconds
        self.save_to_db()
        if self.pool_max_orp_daily_seconds_cb is not None:
            self.pool_max_orp_daily_seconds_cb()

    def set_pool_ph_auto_injection_disabled(self, state: bool):
        """
        Sets the pool ph auto-injection state
        Args:
            state: state disabled or enabled

        Returns:

        """
        self.pool_ph_auto_injection_disabled = state
        self.save_to_db()
        if self.pool_ph_auto_injection_disabled_cb is not None:
            self.pool_ph_auto_injection_disabled_cb()


    def set_pool_orp_auto_injection_disabled(self, state: bool):
        """
        Sets the pool orp auto-injection state
        Args:
            state: state disabled or enabled

        Returns:

        """
        self.pool_orp_auto_injection_disabled = state
        self.save_to_db()
        if self.pool_orp_auto_injection_disabled_cb is not None:
            self.pool_orp_auto_injection_disabled_cb()

    def set_pool_ph_setpoint(self, setpoint: float):
        """
        Sets the pool ph setpoint
        Args:
            setpoint: Setpoint to be utilized

        Returns:

        """
        self.pool_ph_setpoint = setpoint
        self.save_to_db()
        if self.pool_ph_setpoint_cb is not None:
            self.pool_ph_setpoint_cb()

    def set_pool_orp_mv_setpoint(self, setpoint: float):
        """
        Sets the pool orp mv setpoint
        Args:
            setpoint: Setpoint to be utilized

        Returns:

        """
        self.pool_orp_mv_setpoint = setpoint
        self.save_to_db()
        if self.pool_orp_mv_setpoint_cb is not None:
            self.pool_orp_mv_setpoint_cb()

    def set_pool_hydrodynamic_factor(self, factor: int):
        """
        Sets the pool hydrodynamic factor
        Args:
            factor: Factor to be utilized

        Returns:

        """
        self.pool_hydrodynamic_factor = factor

        self.save_to_db()

    def set_pool_recirculation_period(self, period: float):
        """
        Sets the pool recirculation period in hours.
        Args:
            period: Period in hours to be utilized

        Returns:

        """
        self.pool_recirculation_period = period

        self.save_to_db()

    def set_daily_filter_allowed_hours(self, hours):
        """
        Sets the daily allowed hours of filtering.
        Args:
            hours: List with the allowed hours

        Returns:

        """
        self.daily_filter_allowed_hours = hours
        self.save_to_db()

        if self.daily_filter_allowed_hours_cb is not None:
            self.daily_filter_allowed_hours_cb()



    def set_sensor_refresh_minutes(self, minutes):
        """
        Sets the time in minutes in which we will update all data from water sensors.

        Args:
            minutes: Minutes of waiting

        Returns:

        """
        if minutes <= 0:
            minutes = cfg.SENSOR_REFRESH_MIN_MINUTES
        if minutes > 20:
            minutes = cfg.SENSOR_REFRESH_MAX_MINUTES

        self.sensor_refresh_minutes = minutes

        if self.sensor_refresh_minutes_cb is not None:
            self.sensor_refresh_minutes_cb()

        self.save_to_db()

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("pool_config_data")
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]
            self.sensor_refresh_minutes = record["sensor_refresh_minutes"]
            self.daily_filter_allowed_hours = record["daily_filter_allowed_hours"]
            self.pool_hydrodynamic_factor = record["pool_hydrodynamic_factor"]
            self.pool_recirculation_period = record["pool_recirculation_period"]
            self.pool_orp_mv_setpoint = record["pool_orp_mv_setpoint"]
            self.pool_ph_setpoint = record["pool_ph_setpoint"]
            self.pool_orp_auto_injection_disabled = record["pool_orp_auto_injection_disabled"]
            self.pool_ph_auto_injection_disabled = record["pool_ph_auto_injection_disabled"]
            self.pool_max_orp_daily_seconds = record["pool_max_orp_daily_seconds"]
            self.pool_max_ph_daily_seconds = record["pool_max_ph_daily_seconds"]
            self.pool_flow_k_factor = record["pool_flow_k_factor"]
            self.pool_fill_start_level = record["pool_fill_start_level"]
            self.pool_fill_end_level = record["pool_fill_end_level"]
            self.pool_max_daily_water_volume_m3 = record["pool_max_daily_water_volume_m3"]
            self.pool_fill_volume_between_checks = record["pool_fill_volume_between_checks"]
            self.pool_fill_seconds_wait = record["pool_fill_seconds_wait"]
            self.pool_auto_lights_on = record["pool_auto_lights_on"]
            self.pool_auto_lights_on_command_sequence = record["pool_auto_lights_on_command_sequence"]
            logging.log(logging.INFO, strings.LOG_CFG_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_CFG_NOT_LOADED)

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            col = db.get_db().get_collection("pool_config_data")

            # Create a new SensorData object in database and save all the data
            poolconfigdb = PoolConfigData()

            poolconfigdb.datetime = datetime.datetime.utcnow()
            poolconfigdb.sensor_refresh_minutes = self.sensor_refresh_minutes
            poolconfigdb.daily_filter_allowed_hours = self.daily_filter_allowed_hours
            poolconfigdb.pool_hydrodynamic_factor = self.pool_hydrodynamic_factor
            poolconfigdb.pool_recirculation_period = self.pool_recirculation_period
            poolconfigdb.pool_orp_mv_setpoint = self.pool_orp_mv_setpoint
            poolconfigdb.pool_ph_setpoint = self.pool_ph_setpoint
            poolconfigdb.pool_orp_auto_injection_disabled = self.pool_orp_auto_injection_disabled
            poolconfigdb.pool_ph_auto_injection_disabled = self.pool_ph_auto_injection_disabled
            poolconfigdb.pool_max_orp_daily_seconds = self.pool_max_orp_daily_seconds
            poolconfigdb.pool_max_ph_daily_seconds = self.pool_max_ph_daily_seconds
            poolconfigdb.pool_flow_k_factor = self.pool_flow_k_factor
            poolconfigdb.pool_fill_start_level = self.pool_fill_start_level
            poolconfigdb.pool_fill_end_level = self.pool_fill_end_level
            poolconfigdb.pool_max_daily_water_volume_m3 = self.pool_max_daily_water_volume_m3
            poolconfigdb.pool_fill_volume_between_checks = self.pool_fill_volume_between_checks
            poolconfigdb.pool_fill_seconds_wait = self.pool_fill_seconds_wait
            poolconfigdb.pool_auto_lights_on = self.pool_auto_lights_on
            poolconfigdb.pool_auto_lights_on_command_sequence = self.pool_auto_lights_on_command_sequence

            col.replace_one({}, poolconfigdb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass
