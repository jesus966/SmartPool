import datetime
import logging

import pymongo

import src.config.configconstants as cfg
import src.strings_constants.strings as strings
from src.actuators import acidPump
from src.actuators import auxOut
from src.actuators import bleachPump
from src.actuators import fillValve
from src.actuators import filterPump
from src.database.db import db
from src.database.models import ActuatorControlData
from src.exceptions.emergencystopexception import EmergencyStopException
from src.exceptions.manualmodeexception import ManualModeException
from src.exceptions.unknownactuatorexception import UnknownActuatorException
from src.models import Timer, bleachTank, acidTank
from src.sensors import pumpSensor, emergencyStopSensor

from pymongo import errors

class ActuatorControl:
    """
    This class monitors and controls all the actuators from the pool.
    """

    ''' Pumps automatic or manual control '''
    PUMP_AUTOMATIC_CONTROL = True

    ''' Current state of each pump '''
    FILTER_PUMP_REAL_STATE = False
    FILTER_PUMP_TEORIC_STATE = False
    BLEACH_PUMP_STATE = False
    ACID_PUMP_STATE = False
    AUX_OUT_STATE = False

    ''' Fill valve automatic or manual control '''
    VALVE_AUTOMATIC_CONTROL = True

    ''' Current state of the fill actuator '''
    FILL_VALVE_STATE = False

    ''' Timer that every second update's actuator statistics '''
    __statisticsTimer__ = None

    ''' Variable for storing and update the current day '''
    __day__ = None

    ''' Statistics variables '''
    FILTER_PUMP_ON_REAL_SECONDS = 0
    FILTER_PUMP_ON_TOTAL_SECONDS = 0
    FILTER_PUMP_ON_AUTO_SECONDS = 0
    FILTER_PUMP_ON_MANUAL_SECONDS = 0
    FILTER_PUMP_SEC_SINCE_LAST_ON = 0

    BLEACH_PUMP_ON_TOTAL_SECONDS = 0
    BLEACH_PUMP_ON_AUTO_SECONDS = 0
    BLEACH_PUMP_ON_MANUAL_SECONDS = 0
    BLEACH_PUMP_SEC_SINCE_LAST_ON = 0

    ACID_PUMP_ON_TOTAL_SECONDS = 0
    ACID_PUMP_ON_AUTO_SECONDS = 0
    ACID_PUMP_ON_MANUAL_SECONDS = 0
    ACID_PUMP_SEC_SINCE_LAST_ON = 0

    AUX_OUT_ON_TOTAL_SECONDS = 0
    AUX_OUT_ON_AUTO_SECONDS = 0
    AUX_OUT_ON_MANUAL_SECONDS = 0
    AUX_OUT_SEC_SINCE_LAST_ON = 0

    FILL_VALVE_ON_TOTAL_SECONDS = 0
    FILL_VALVE_ON_AUTO_SECONDS = 0
    FILL_VALVE_ON_MANUAL_SECONDS = 0
    FILL_VALVE_SEC_SINCE_LAST_ON = 0

    ''' Variables for emergency stop '''
    IN_EMERGENCY_STOP = False
    EMERGENCY_STOP_CAUSE = None

    def __init__(self):
        """
        Constructor of the class
        """
        logging.log(logging.INFO, strings.LOG_ACT_CTR_INSTANTIATED)
        pumpSensor.add_callback(self.__update_real_state__)
        self.__statisticsTimer__ = Timer(self.__statistics__)
        self.__statisticsTimer__.start()
        self.__day__ = datetime.datetime.utcnow().day
        self.load_from_db()

    def emergency_stop(self, cause, resume=False):
        """
        This method preform an emergency stop in all the pumps.

        Args:
            cause: The cause of this emergency stop or resume.
            resume: If it is True, it resumes normal operation.

        Returns:

        """
        if not resume and not self.IN_EMERGENCY_STOP:
            # Stop ALL pumps
            acidPump.setstate(False)
            bleachPump.setstate(False)
            filterPump.setstate(False)

            self.EMERGENCY_STOP_CAUSE = cause
            self.IN_EMERGENCY_STOP = True

            logging.log(logging.WARNING, strings.LOG_ACT_CTR_ESTOP)

        if resume and self.IN_EMERGENCY_STOP:
            # Restore the previous state of the pumps.
            filterPump.setstate(self.FILTER_PUMP_TEORIC_STATE)
            bleachPump.setstate(self.BLEACH_PUMP_STATE)
            acidPump.setstate(self.ACID_PUMP_STATE)

            self.EMERGENCY_STOP_CAUSE = None
            self.IN_EMERGENCY_STOP = False

            logging.log(logging.WARNING, strings.LOG_ACT_CTR_RESUME)

        self.save_to_db()

    def __statistics__(self):
        """
        This method is called by a Timer every second to update daily statistics
        of the actuators.

        Returns:

        """
        if not self.AUX_OUT_STATE:
            self.AUX_OUT_SEC_SINCE_LAST_ON = 0

        if not self.FILL_VALVE_STATE:
            self.FILL_VALVE_SEC_SINCE_LAST_ON = 0

        if not self.IN_EMERGENCY_STOP:
            if not self.FILTER_PUMP_REAL_STATE:
                self.FILTER_PUMP_SEC_SINCE_LAST_ON = 0

            if not self.BLEACH_PUMP_STATE:
                self.BLEACH_PUMP_SEC_SINCE_LAST_ON = 0

            if not self.ACID_PUMP_STATE:
                self.ACID_PUMP_SEC_SINCE_LAST_ON = 0

        else:
            self.FILTER_PUMP_SEC_SINCE_LAST_ON = 0
            self.BLEACH_PUMP_SEC_SINCE_LAST_ON = 0
            self.ACID_PUMP_SEC_SINCE_LAST_ON = 0

        # Check if this is a new day
        if self.__day__ != datetime.datetime.utcnow().day:
            # It's a new day, clear all the statistics
            self.__day__ = datetime.datetime.utcnow().day

            self.FILTER_PUMP_ON_REAL_SECONDS = 0
            self.FILTER_PUMP_ON_TOTAL_SECONDS = 0
            self.FILTER_PUMP_ON_AUTO_SECONDS = 0
            self.FILTER_PUMP_ON_MANUAL_SECONDS = 0

            self.BLEACH_PUMP_ON_TOTAL_SECONDS = 0
            self.BLEACH_PUMP_ON_AUTO_SECONDS = 0
            self.BLEACH_PUMP_ON_MANUAL_SECONDS = 0

            self.ACID_PUMP_ON_TOTAL_SECONDS = 0
            self.ACID_PUMP_ON_AUTO_SECONDS = 0
            self.ACID_PUMP_ON_MANUAL_SECONDS = 0

            self.AUX_OUT_ON_TOTAL_SECONDS = 0
            self.AUX_OUT_ON_AUTO_SECONDS = 0
            self.AUX_OUT_ON_MANUAL_SECONDS = 0

            self.FILL_VALVE_ON_TOTAL_SECONDS = 0
            self.FILL_VALVE_ON_AUTO_SECONDS = 0
            self.FILL_VALVE_ON_MANUAL_SECONDS = 0

            # Save statistics to database
            self.save_to_db()

        else:
            # It isn't a new day, update statistics

            if self.FILTER_PUMP_REAL_STATE:
                self.FILTER_PUMP_ON_REAL_SECONDS += 1
                self.FILTER_PUMP_SEC_SINCE_LAST_ON += 1
                # Save statistics to database
                self.save_to_db()

            if self.PUMP_AUTOMATIC_CONTROL:
                if self.FILTER_PUMP_TEORIC_STATE:
                    self.FILTER_PUMP_ON_AUTO_SECONDS += 1
                    self.FILTER_PUMP_ON_TOTAL_SECONDS = self.FILTER_PUMP_ON_AUTO_SECONDS \
                                                        + self.FILTER_PUMP_ON_MANUAL_SECONDS
                    # Save statistics to database
                    self.save_to_db()

                if self.BLEACH_PUMP_STATE:
                    self.BLEACH_PUMP_ON_AUTO_SECONDS += 1
                    self.BLEACH_PUMP_SEC_SINCE_LAST_ON += 1
                    self.BLEACH_PUMP_ON_TOTAL_SECONDS = self.BLEACH_PUMP_ON_AUTO_SECONDS \
                                                        + self.BLEACH_PUMP_ON_MANUAL_SECONDS
                    bleachTank.decrease_value(cfg.TANK_SEC_DECREASE_VALUE_LITERS)
                    # Save statistics to database
                    self.save_to_db()

                if self.ACID_PUMP_STATE:
                    self.ACID_PUMP_ON_AUTO_SECONDS += 1
                    self.ACID_PUMP_SEC_SINCE_LAST_ON += 1
                    self.ACID_PUMP_ON_TOTAL_SECONDS = self.ACID_PUMP_ON_AUTO_SECONDS \
                                                      + self.ACID_PUMP_ON_MANUAL_SECONDS
                    acidTank.decrease_value(cfg.TANK_SEC_DECREASE_VALUE_LITERS)
                    # Save statistics to database
                    self.save_to_db()

                if self.AUX_OUT_STATE:
                    self.AUX_OUT_ON_AUTO_SECONDS += 1
                    self.AUX_OUT_SEC_SINCE_LAST_ON += 1
                    self.AUX_OUT_ON_TOTAL_SECONDS = self.AUX_OUT_ON_AUTO_SECONDS \
                                                    + self.AUX_OUT_ON_MANUAL_SECONDS
                    # Save statistics to database
                    self.save_to_db()

            else:
                if self.FILTER_PUMP_TEORIC_STATE:
                    self.FILTER_PUMP_ON_MANUAL_SECONDS += 1
                    self.FILTER_PUMP_ON_TOTAL_SECONDS = self.FILTER_PUMP_ON_AUTO_SECONDS \
                                                        + self.FILTER_PUMP_ON_MANUAL_SECONDS
                    # Save statistics to database
                    self.save_to_db()

                if self.BLEACH_PUMP_STATE:
                    self.BLEACH_PUMP_ON_MANUAL_SECONDS += 1
                    self.BLEACH_PUMP_SEC_SINCE_LAST_ON += 1
                    self.BLEACH_PUMP_ON_TOTAL_SECONDS = self.BLEACH_PUMP_ON_AUTO_SECONDS \
                                                        + self.BLEACH_PUMP_ON_MANUAL_SECONDS
                    bleachTank.decrease_value(cfg.TANK_SEC_DECREASE_VALUE_LITERS)
                    # Save statistics to database
                    self.save_to_db()

                if self.ACID_PUMP_STATE:
                    self.ACID_PUMP_ON_MANUAL_SECONDS += 1
                    self.ACID_PUMP_SEC_SINCE_LAST_ON += 1
                    self.ACID_PUMP_ON_TOTAL_SECONDS = self.ACID_PUMP_ON_AUTO_SECONDS \
                                                      + self.ACID_PUMP_ON_MANUAL_SECONDS
                    acidTank.decrease_value(cfg.TANK_SEC_DECREASE_VALUE_LITERS)
                    # Save statistics to database
                    self.save_to_db()

                if self.AUX_OUT_STATE:
                    self.AUX_OUT_ON_MANUAL_SECONDS += 1
                    self.AUX_OUT_SEC_SINCE_LAST_ON += 1
                    self.AUX_OUT_ON_TOTAL_SECONDS = self.AUX_OUT_ON_AUTO_SECONDS \
                                                    + self.AUX_OUT_ON_MANUAL_SECONDS
                    # Save statistics to database
                    self.save_to_db()

            if self.VALVE_AUTOMATIC_CONTROL and self.FILL_VALVE_STATE:
                self.FILL_VALVE_ON_AUTO_SECONDS += 1
                self.FILL_VALVE_SEC_SINCE_LAST_ON += 1
                self.FILL_VALVE_ON_TOTAL_SECONDS = self.FILL_VALVE_ON_AUTO_SECONDS \
                                                   + self.FILL_VALVE_ON_MANUAL_SECONDS
                # Save statistics to database
                self.save_to_db()

            if not self.VALVE_AUTOMATIC_CONTROL and self.FILL_VALVE_STATE:
                self.FILL_VALVE_ON_MANUAL_SECONDS += 1
                self.FILL_VALVE_SEC_SINCE_LAST_ON += 1
                self.FILL_VALVE_ON_TOTAL_SECONDS = self.FILL_VALVE_ON_AUTO_SECONDS \
                                                   + self.FILL_VALVE_ON_MANUAL_SECONDS
                # Save statistics to database
                self.save_to_db()

    def __update_real_state__(self):
        """
        This private function is called when there is an update in the filter pump intensity sensor.

        Returns:

        """

        if pumpSensor.value is not None and pumpSensor.value > 0:
            self.FILTER_PUMP_REAL_STATE = True
        else:
            self.FILTER_PUMP_REAL_STATE = False

        # Save statistics to database
        self.save_to_db()

    def setstate(self, actuator: str, state: bool, automatic=True):
        """
        Set's the current actuator state

        Args:
            actuator: Name of the actuator to control
            state: New actuator state
            automatic: If it's false, it's a manual change of state

        Returns: None

        """
        # Only for the pumps, avoid changing the state when we are in emergency stop.

        if self.IN_EMERGENCY_STOP and (actuator == cfg.FILTER_PUMP or actuator == cfg.BLEACH_PUMP
                                       or actuator == cfg.ACID_PUMP):
            raise EmergencyStopException

        if actuator == cfg.FILTER_PUMP or actuator == cfg.BLEACH_PUMP \
                or actuator == cfg.ACID_PUMP or actuator == cfg.AUX_OUT:
            ''' 
                If it is a manual change of state, change
                all pumps control state to MANUAL.
            '''
            if not automatic:
                self.PUMP_AUTOMATIC_CONTROL = False

            '''
                If we are on manual control and this is an
                automatic change of state, ignore it
            '''
            if not self.PUMP_AUTOMATIC_CONTROL and automatic:
                logging.log(logging.WARNING, strings.LOG_ACT_CTR_NOT_ALLOWED, actuator, state)
                raise ManualModeException

        if actuator == cfg.FILTER_PUMP:

            # Change the state
            filterPump.setstate(state)
            self.FILTER_PUMP_TEORIC_STATE = state

        elif actuator == cfg.BLEACH_PUMP:

            bleachPump.setstate(state)
            self.BLEACH_PUMP_STATE = state

        elif actuator == cfg.ACID_PUMP:

            # Change the state
            acidPump.setstate(state)
            self.ACID_PUMP_STATE = state

        elif actuator == cfg.AUX_OUT:

            # Change the state
            auxOut.setstate(state)
            self.AUX_OUT_STATE = state

        elif actuator == cfg.FILL_VALVE:

            ''' 
                If it is a manual change of state, change
                all pumps control state to MANUAL.
            '''
            if not automatic:
                self.VALVE_AUTOMATIC_CONTROL = False

            '''
                If we are on manual control and this is an
                automatic change of state, ignore it
            '''
            if not self.VALVE_AUTOMATIC_CONTROL and automatic:
                logging.log(logging.WARNING, strings.LOG_ACT_CTR_NOT_ALLOWED, actuator, state)
                raise ManualModeException
            else:
                # Change the state
                fillValve.setstate(state)
                self.FILL_VALVE_STATE = state

        else:
            raise UnknownActuatorException

        if automatic:
            logging.log(logging.INFO, strings.LOG_ACT_CTR_STATE_CHANGED, actuator, state, strings.LOG_ACT_CTR_AUTOMATIC)
        else:
            logging.log(logging.INFO, strings.LOG_ACT_CTR_STATE_CHANGED, actuator, state, strings.LOG_ACT_CTR_MANUAL)

        # Save statistics to database
        self.save_to_db()

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("actuator_control_data")
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]

            self.PUMP_AUTOMATIC_CONTROL = record["pump_automatic_control"]
            self.VALVE_AUTOMATIC_CONTROL = record["valve_automatic_control"]

            cause = record["emergency_stop_cause"]

            if cause == "None" or cause == cfg.ESTOP_CAUSE_SENSOR:
                # Check the current state of the emergency stop sensor
                if emergencyStopSensor.value:
                    self.emergency_stop(cfg.ESTOP_CAUSE_SENSOR)
                else:
                    self.emergency_stop(None, resume=True)
            else:
                self.EMERGENCY_STOP_CAUSE = record["emergency_stop_cause"]
                self.IN_EMERGENCY_STOP = record["in_emergency_stop"]

            # Apply the last state of actuators, if we aren't in emergency stop
            if not self.IN_EMERGENCY_STOP:
                filterPump.setstate(self.FILTER_PUMP_TEORIC_STATE)
                bleachPump.setstate(self.BLEACH_PUMP_STATE)
                acidPump.setstate(self.ACID_PUMP_STATE)

            auxOut.setstate(self.AUX_OUT_STATE)
            fillValve.setstate(self.FILL_VALVE_STATE)

            # If the last record day is today, load all data
            if self.__day__ == record["datetime"].day:

                self.FILTER_PUMP_ON_REAL_SECONDS = record["filter_pump_on_real_seconds"]
                self.FILTER_PUMP_ON_TOTAL_SECONDS = record["filter_pump_on_total_seconds"]
                self.FILTER_PUMP_ON_AUTO_SECONDS = record["filter_pump_on_auto_seconds"]
                self.FILTER_PUMP_ON_MANUAL_SECONDS = record["filter_pump_on_manual_seconds"]

                self.BLEACH_PUMP_ON_TOTAL_SECONDS = record["bleach_pump_on_total_seconds"]
                self.BLEACH_PUMP_ON_AUTO_SECONDS = record["bleach_pump_on_auto_seconds"]
                self.BLEACH_PUMP_ON_MANUAL_SECONDS = record["bleach_pump_on_manual_seconds"]

                self.ACID_PUMP_ON_TOTAL_SECONDS = record["acid_pump_on_total_seconds"]
                self.ACID_PUMP_ON_AUTO_SECONDS = record["acid_pump_on_auto_seconds"]
                self.ACID_PUMP_ON_MANUAL_SECONDS = record["acid_pump_on_manual_seconds"]

                self.AUX_OUT_ON_TOTAL_SECONDS = record["aux_out_on_total_seconds"]
                self.AUX_OUT_ON_AUTO_SECONDS = record["aux_out_on_auto_seconds"]
                self.AUX_OUT_ON_MANUAL_SECONDS = record["aux_out_on_manual_seconds"]

                self.FILL_VALVE_ON_TOTAL_SECONDS = record["fill_valve_on_total_seconds"]
                self.FILL_VALVE_ON_AUTO_SECONDS = record["fill_valve_on_auto_seconds"]
                self.FILL_VALVE_ON_MANUAL_SECONDS = record["fill_valve_on_manual_seconds"]

                logging.log(logging.INFO, strings.LOG_ACT_CTR_LOADED)
            else:
                logging.log(logging.INFO, strings.LOG_ACT_CTR_NOT_LOADED)
        except IndexError:
            logging.log(logging.INFO, strings.LOG_ACT_CTR_LOAD_FAIL)

    def save_to_db(self):
        """
        This method saves or updates the database.

        Args:

        Returns:

        """
        try:
            col = db.get_db().get_collection("actuator_control_data")

            # Create a new SensorData object in database and save all the data
            actuatordb = ActuatorControlData()

            actuatordb.datetime = datetime.datetime.utcnow()

            actuatordb.in_emergency_stop = self.IN_EMERGENCY_STOP

            if self.EMERGENCY_STOP_CAUSE is None:
                actuatordb.emergency_stop_cause = "None"
            else:
                actuatordb.emergency_stop_cause = self.EMERGENCY_STOP_CAUSE

            actuatordb.pump_automatic_control = self.PUMP_AUTOMATIC_CONTROL
            actuatordb.valve_automatic_control = self.VALVE_AUTOMATIC_CONTROL
            actuatordb.filter_pump_teoric_state = self.FILTER_PUMP_TEORIC_STATE
            actuatordb.bleach_pump_state = self.BLEACH_PUMP_STATE
            actuatordb.acid_pump_state = self.ACID_PUMP_STATE
            actuatordb.aux_out_state = self.ACID_PUMP_STATE
            actuatordb.fill_valve_state = self.FILL_VALVE_STATE

            actuatordb.filter_pump_on_real_seconds = self.FILTER_PUMP_ON_REAL_SECONDS
            actuatordb.filter_pump_on_total_seconds = self.FILTER_PUMP_ON_TOTAL_SECONDS
            actuatordb.filter_pump_on_auto_seconds = self.FILTER_PUMP_ON_AUTO_SECONDS
            actuatordb.filter_pump_on_manual_seconds = self.FILTER_PUMP_ON_MANUAL_SECONDS

            actuatordb.bleach_pump_on_total_seconds = self.BLEACH_PUMP_ON_TOTAL_SECONDS
            actuatordb.bleach_pump_on_auto_seconds = self.BLEACH_PUMP_ON_AUTO_SECONDS
            actuatordb.bleach_pump_on_manual_seconds = self.BLEACH_PUMP_ON_MANUAL_SECONDS

            actuatordb.acid_pump_on_total_seconds = self.ACID_PUMP_ON_TOTAL_SECONDS
            actuatordb.acid_pump_on_auto_seconds = self.ACID_PUMP_ON_AUTO_SECONDS
            actuatordb.acid_pump_on_manual_seconds = self.ACID_PUMP_ON_MANUAL_SECONDS

            actuatordb.aux_out_on_total_seconds = self.AUX_OUT_ON_TOTAL_SECONDS
            actuatordb.aux_out_on_auto_seconds = self.AUX_OUT_ON_AUTO_SECONDS
            actuatordb.aux_out_on_manual_seconds = self.AUX_OUT_ON_MANUAL_SECONDS

            actuatordb.fill_valve_on_total_seconds = self.FILL_VALVE_ON_TOTAL_SECONDS
            actuatordb.fill_valve_on_auto_seconds = self.FILL_VALVE_ON_AUTO_SECONDS
            actuatordb.fill_valve_on_manual_seconds = self.FILL_VALVE_ON_MANUAL_SECONDS

            col.replace_one({}, actuatordb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass