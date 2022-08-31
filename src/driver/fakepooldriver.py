import logging
import random

import src.config.configconstants as cfg
import src.strings_constants.strings as strings
from src.exceptions.unknownactuatorexception import UnknownActuatorException
from src.models import Timer
from src.sensors import temperatureSensor, phSensor, tdsSensor, orpSensor, pumpSensor


class FakePoolDriver:
    """
    Class that implements the pool driver
    """

    '''
    Callback functions to be called when a sensor value is changed
    '''
    callback_list_temp = []
    callback_list_light = []
    callback_list_pump = []
    callback_list_general = []
    callback_list_voltage = []
    callback_list_ph = []
    callback_list_orp = []
    callback_list_tds = []
    callback_list_sandp = []
    callback_list_diatomnsp = []
    callback_list_flow = []
    callback_list_wl1 = []
    callback_list_emergency = []

    filterpump = False

    def __init__(self):
        """
        The constructor of this class initializes the arduino board.
        It throws a BoardInitException when some problem is found initializing the board.
        """
        logging.log(logging.INFO, strings.LOG_DRIVER_INSTANTIATED)
        t = Timer(self.__fake__, period=10)
        t.start()
        t2 = Timer(self.__fake2__, period=0.5).start()

    def __fake2__(self):
        if self.filterpump:
            if self.callback_list_pump is not None:
                pumpSensor.add_value(7, save=False)

    def __fake__(self):
        if self.callback_list_temp is not None:
            # temp = random.randrange(5, 6, 1)
            temp = 15
            temperatureSensor.add_value(temp)

        if self.callback_list_ph is not None:
            ph = 7 + (random.randrange(0, 1000, 100) / 1000)
            phSensor.add_value(ph)

        if self.callback_list_orp is not None:
            orp = random.randrange(600, 800, 10)
            orpSensor.add_value(orp)

        if self.callback_list_tds is not None:
            tds = random.randrange(0, 1000, 10)
            tdsSensor.add_value(tds)

    def set_state(self, actuator, state):
        """
        This function set the state of a given actuator
        """
        if actuator == cfg.FILTER_PUMP:
            self.filterpump = state
            if not state:
                if self.callback_list_pump is not None:
                    pumpSensor.add_value(0, save=False)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.FILTER_PUMP, state)
        elif actuator == cfg.BLEACH_PUMP:
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.BLEACH_PUMP, state)
        elif actuator == cfg.ACID_PUMP:
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.ACID_PUMP, state)
        elif actuator == cfg.AUX_OUT:
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.AUX_OUT, state)
        elif actuator == cfg.FILL_VALVE:
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.FILL_VALVE, state)
        else:
            raise UnknownActuatorException

    def getstate(self, sensor: str) -> bool:
        """
        This function gets the current state of a given sensor
        """
        return False

    def set_sensor_callback(self, sensor: str, function, edge=None) -> None:
        """
        This function calls a given function when a sensor state changes, or when a new sensor
        value is obtained.
        """
        if function is not None:
            if sensor == cfg.TEMP_SENSOR:
                self.callback_list_temp.append(function)
            elif sensor == cfg.LIGHT_SENSOR:
                self.callback_list_light.append(function)
            elif sensor == cfg.PUMP_SENSOR:
                self.callback_list_pump.append(function)
            elif sensor == cfg.GENERAL_SENSOR:
                self.callback_list_general.append(function)
            elif sensor == cfg.VOLTAGE_SENSOR:
                self.callback_list_voltage.append(function)
            elif sensor == cfg.PH_SENSOR:
                self.callback_list_ph.append(function)
            elif sensor == cfg.ORP_SENSOR:
                self.callback_list_orp.append(function)
            elif sensor == cfg.TDS_SENSOR:
                self.callback_list_tds.append(function)
            elif sensor == cfg.SAND_PRESSURE_SENSOR:
                self.callback_list_sandp.append(function)
            elif sensor == cfg.DIATOMS_PRESSURE_SENSOR:
                self.callback_list_diatomnsp.append(function)
            elif sensor == cfg.FLOW_SENSOR:
                self.callback_list_flow.append(function)
            elif sensor == cfg.WATER_LEVEL_SENSOR:
                self.callback_list_wl1.append(function)
            elif sensor == cfg.EMERGENCY_STOP_SENSOR:
                self.callback_list_emergency.append(function)
