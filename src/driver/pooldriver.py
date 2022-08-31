import logging
import threading
import time
from itertools import accumulate
import numpy as np
import serial
import src.config.configconstants as cfg
import src.strings_constants.strings as strings
from src.exceptions.boardinitexception import BoardInitException
from src.exceptions.unknownactuatorexception import UnknownActuatorException
from src.models import Timer
from src.sensors import temperatureSensor, pumpSensor, generalSensor, voltageSensor, phSensor, orpSensor, \
    tdsSensor, sandPressureSensor, diatomsPressureSensor, waterLevelSensor_1, waterLevelSensor_2, waterLevelSensor_3, \
    waterLevelSensor_4, waterLevelSensor_5, waterLevelSensor_6, emergencyStopSensor, lightSensor
from src.sensors.subtypes import flowSensor

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils

    fake_rpigpio.utils.install()
    import RPi.GPIO as GPIO


class PoolDriver:
    """
    Class that implements the pool driver
    """

    ''' Arduino and serial mappings '''
    _arduino = None
    _SERIAL_PORT = '/dev/ttyS0'
    _BAUD_RATE = 250000

    _TEMP_SENSOR = '/sys/bus/w1/devices/28-031683c616ff/w1_slave'
    _VCC = 5.2

    ''' Sensor calibrations '''
    M_PH = 2.06896
    B_PH = 2.94482

    M_ORP = -1
    B_ORP = 2.09

    K_TDS = 0.79

    B_SAND_PRESSURE = -1.25
    M_SAND_PRESSURE = 2.5
    OFFSET_SAND_PRESSURE = 0.47

    B_DIATOMS_PRESSURE = -1.25
    M_DIATOMS_PRESSURE = 2.5
    OFFSET_DIATOMS_PRESSURE = 0.48

    ''' GPIO PINS MAPPINGS '''
    _PIN_EMERGENCY_STOP = 25
    _PIN_LEVEL_SENSOR_1 = 9
    _PIN_LEVEL_SENSOR_2 = 27
    _PIN_LEVEL_SENSOR_3 = 26
    _PIN_LEVEL_SENSOR_4 = 24
    _PIN_LEVEL_SENSOR_5 = 23
    _PIN_LEVEL_SENSOR_6 = 22
    _PIN_FLOW_SENSOR = 0
    _PIN_FLOW_SENSOR_2 = 7
    _PIN_FLOW_SENSOR_3 = 8
    _PIN_BUZZER = 11
    _PIN_LED_1 = 21
    _PIN_LIGHT_SENSOR = 20

    _PIN_PUMP_FILTER = 1
    _PIN_PUMP_BLEACH = 16
    _PIN_PUMP_ACID = 6
    _PIN_AUX_OUT = 17
    _PIN_FILL_VALVE = 19

    _thread_adc = None
    _sensors_timer = None

    # Vector that stores raw ADC channel data
    _raw_data = np.zeros((8, 100))

    # Vector that stores ADC channel data converted to volts
    _adc_volts_data_ph = np.array([])
    _adc_volts_data_orp = np.array([])
    _adc_volts_data_sfp = np.array([])
    _adc_volts_data_dfp = np.array([])
    _adc_volts_data_tds = np.array([])
    _adc_volts_last_rms_pump = 0
    _adc_volts_last_rms_general = 0
    _adc_volts_last_rms_voltage = 0

    last_orp_voltage = 0
    last_ph_voltage = 0
    last_tds_voltage = 0
    last_sand_pressure_voltage = 0
    last_diatoms_pressure_voltage = 0

    IN_CALIBRATION_MODE = False

    def __init__(self):
        """
        The constructor of this class initializes the arduino board.
        It throws a BoardInitException when some problem is found initializing the board.
        """
        # Initialize GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Input pins
        GPIO.setup(self._PIN_EMERGENCY_STOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._PIN_LIGHT_SENSOR, GPIO.IN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_LEVEL_SENSOR_6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_FLOW_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_FLOW_SENSOR_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._PIN_FLOW_SENSOR_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Output pins
        GPIO.setup(self._PIN_PUMP_FILTER, GPIO.OUT)
        GPIO.setup(self._PIN_PUMP_BLEACH, GPIO.OUT)
        GPIO.setup(self._PIN_PUMP_ACID, GPIO.OUT)
        GPIO.setup(self._PIN_AUX_OUT, GPIO.OUT)
        GPIO.setup(self._PIN_FILL_VALVE, GPIO.OUT)
        GPIO.setup(self._PIN_BUZZER, GPIO.OUT)
        GPIO.setup(self._PIN_LED_1, GPIO.OUT)

        # Set output pins state
        GPIO.output(self._PIN_PUMP_FILTER, False)
        GPIO.output(self._PIN_PUMP_BLEACH, False)
        GPIO.output(self._PIN_PUMP_ACID, False)
        GPIO.output(self._PIN_AUX_OUT, False)
        GPIO.output(self._PIN_FILL_VALVE, False)
        GPIO.output(self._PIN_BUZZER, False)
        GPIO.output(self._PIN_LED_1, False)

        # Set current level sensor values
        waterLevelSensor_1.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_1)))
        waterLevelSensor_2.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_2)))
        waterLevelSensor_3.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_3)))
        waterLevelSensor_4.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_4)))
        waterLevelSensor_5.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_5)))
        waterLevelSensor_6.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_6)))
        emergencyStopSensor.add_value(not bool(GPIO.input(self._PIN_EMERGENCY_STOP)))
        lightSensor.add_value(bool(GPIO.input(self._PIN_LIGHT_SENSOR)))

        # Set ISRs
        GPIO.add_event_detect(self._PIN_EMERGENCY_STOP, GPIO.BOTH, callback=self._emergency_stop)
        GPIO.add_event_detect(self._PIN_FLOW_SENSOR, GPIO.RISING, callback=self._flow_tick)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_1, GPIO.BOTH, callback=self._level_tick_1)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_2, GPIO.BOTH, callback=self._level_tick_2)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_3, GPIO.BOTH, callback=self._level_tick_3)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_4, GPIO.BOTH, callback=self._level_tick_4)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_5, GPIO.BOTH, callback=self._level_tick_5)
        GPIO.add_event_detect(self._PIN_LEVEL_SENSOR_6, GPIO.BOTH, callback=self._level_tick_6)
        GPIO.add_event_detect(self._PIN_LIGHT_SENSOR, GPIO.BOTH, callback=self._light_tick)

        # Start arduino
        self._init_arduino()

        # Create a thread that samples ADC data from arduino
        self._thread_adc = threading.Thread(target=self._get_adc, name='ADC Thread')
        self._thread_adc.daemon = True
        self._thread_adc.start()

        # Start a timer that gets sensor data
        self._sensors_timer = Timer(self._update_sensors)
        self._sensors_timer.start()

        logging.log(logging.INFO, strings.LOG_DRIVER_INSTANTIATED)

    def _light_tick(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        lightSensor.add_value(bool(GPIO.input(self._PIN_LIGHT_SENSOR)))

    def _level_tick_6(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_6.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_6)))

    def _level_tick_5(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_5.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_5)))

    def _level_tick_4(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_4.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_4)))

    def _level_tick_3(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_3.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_3)))

    def _level_tick_2(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_2.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_2)))

    def _level_tick_1(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        waterLevelSensor_1.add_value(bool(GPIO.input(self._PIN_LEVEL_SENSOR_1)))

    @staticmethod
    def _flow_tick(pin):
        """
        This method is called every time that the sensor is triggered
        """
        flowSensor.add_tick()

    def _emergency_stop(self, pin):
        """
        This method is called every time that the sensor is triggered
        """
        emergencyStopSensor.add_value(not bool(GPIO.input(self._PIN_EMERGENCY_STOP)))

    def _update_sensors(self):
        """
        This method is called periodically to convert voltage values of sensors to actual sensor data
        and adds the new data to every sensor object.
        """
        # Get mean of volts of ORP sensor, and get its value
        voltage_mean = np.mean(self._adc_volts_data_orp)
        self._adc_volts_data_orp = np.array([])  # Reset vector
        self.last_orp_voltage = voltage_mean  # Save last voltage reading
        # Sensor calibration constants
        b = self.B_ORP
        m = self.M_ORP
        x = voltage_mean
        y = (m * x) + b
        orp_value = y * 1000

        # Get mean of volts of PH sensor, and get its value
        voltage_mean = np.mean(self._adc_volts_data_ph)
        self._adc_volts_data_ph = np.array([])  # Reset vector
        self.last_ph_voltage = voltage_mean  # Save last voltage reading
        # Sensor calibration constants
        b = self.B_PH
        m = self.M_PH
        x = voltage_mean
        ph_value = (m * x) + b

        # Get current temperature value
        temperature = self.get_temperature()

        # Get mean of volts of TDS sensor, and get its value
        voltage_mean = np.mean(self._adc_volts_data_tds)
        self._adc_volts_data_tds = np.array([])  # Reset vector
        self.last_tds_voltage = voltage_mean

        if temperature is None:
            compensation_temperature = 25
        else:
            compensation_temperature = temperature

        compensation_coefficient = 1 + 0.02 * (compensation_temperature - 25)
        '''
        # Tds sensor calibration code
        rawECsolution = (342/0.5) * compensation_coefficient
        KValueTemp = rawECsolution / (133.42 * np.power(voltage_mean, 3) -
                    255.86 * np.power(voltage_mean, 2) +
                    857.39 * voltage_mean)
        tds_value = KValueTemp
        print(tds_value)

        '''
        
        tdsValue = (133.42 * np.power(voltage_mean, 3) -
                    255.86 * np.power(voltage_mean, 2) +
                    857.39 * voltage_mean) * self.K_TDS
        
        tds_value = (tdsValue / compensation_coefficient) * 0.5

        # Get mean of volts of sand pressure sensor, and get its value
        voltage_mean = np.mean(self._adc_volts_data_sfp)
        self._adc_volts_data_sfp = np.array([])  # Reset vector
        self.last_sand_pressure_voltage = voltage_mean

        if voltage_mean < self.OFFSET_SAND_PRESSURE*1.1:
            sand_pressure = 0
        else:
            b = self.B_SAND_PRESSURE
            m = self.M_SAND_PRESSURE
            offset = self.OFFSET_SAND_PRESSURE
            sand_pressure = (m * voltage_mean + (0.5 - offset)) + b

        voltage_mean = np.mean(self._adc_volts_data_dfp)
        self._adc_volts_data_dfp = np.array([])  # Reset vector
        self.last_diatoms_pressure_voltage = voltage_mean

        if voltage_mean < self.OFFSET_DIATOMS_PRESSURE*1.1:
            diatoms_pressure = 0
        else:
            b = self.B_DIATOMS_PRESSURE
            m = self.M_DIATOMS_PRESSURE
            offset = self.OFFSET_DIATOMS_PRESSURE
            diatoms_pressure = (m * voltage_mean + (0.5 - offset)) + b

        # Get current intensity and mains voltage

        rms_pump_intensity = self._adc_volts_last_rms_pump
        rms_general_intensity = self._adc_volts_last_rms_general
        rms_mains_voltage = self._adc_volts_last_rms_voltage

        # Ignore noise in the sensors
        if rms_mains_voltage < 0.02:
            rms_mains_voltage = 0

        if rms_pump_intensity < 0.02:
            rms_pump_intensity = 0

        if rms_general_intensity < 0.02:
            rms_general_intensity = 0

        # Calibrate values
        rms_mains_voltage = (rms_mains_voltage * 235) / 1.39
        rms_pump_intensity = rms_pump_intensity * 30
        rms_general_intensity = rms_general_intensity * 30

        # Now, add data to the corresponding sensors
        if not self.IN_CALIBRATION_MODE:
            if temperature is not None and (type(temperature) == int or type(temperature) == float):
                temperatureSensor.add_value(temperature)
            if not np.isnan(rms_pump_intensity):
                pumpSensor.add_value(rms_pump_intensity)
            if not np.isnan(rms_general_intensity):
                generalSensor.add_value(rms_general_intensity)
            if not np.isnan(rms_mains_voltage):
                voltageSensor.add_value(rms_mains_voltage)
            if not np.isnan(ph_value):
                phSensor.add_value(ph_value)
            if not np.isnan(orp_value):
                orpSensor.add_value(orp_value)
            if not np.isnan(tds_value):
                tdsSensor.add_value(tds_value)
            if not np.isnan(sand_pressure):
                sandPressureSensor.add_value(sand_pressure)
            if not np.isnan(diatoms_pressure):
                diatomsPressureSensor.add_value(diatoms_pressure)

    def _init_arduino(self):
        """
        This method starts communications with the board arduino
        """
        try:
            # Start serial port
            self._arduino = serial.Serial(self._SERIAL_PORT, self._BAUD_RATE)

            retries = 10

            while retries > 0:
                # Send reset command to arduino
                self._arduino.write(b'r')
                self._arduino.flushInput()
                self._arduino.flushOutput()

                time.sleep(0.5)

                try:
                    response = self._arduino.readline().decode().replace('\r', '').replace('\n', '')
                except UnicodeDecodeError:
                    response = None

                if response == "Arduino Piscina Version 1.0":
                    retries = -1
                else:
                    retries -= 1

            # If retries reached 0, it was unable to establish connection with arduino
            if retries == 0:
                raise BoardInitException(message="Error while initiating board, max arduino communication retries "
                                                 "reached.")

        except KeyboardInterrupt:
            try:
                self._arduino.close()
            except Exception:
                pass

            raise BoardInitException(message="Error while initiating board, aborted by the user.")

        except Exception as e:
            try:
                self._arduino.close()
            except Exception:
                pass

            raise BoardInitException(message="Error while initiating board: " + str(e))

    def _get_adc(self):
        """
        This method is called within a thread, and it gets the current ADC data from arduino.
        """
        c = 0
        i = 0
        self._arduino.write(b's')  # Start ADC

        while True:
            try:
                # Get current line
                response = self._arduino.readline().decode().replace('\r', '').replace('\n', '')

                if response == "INICIODEDATOS":
                    do_loop = True
                    while do_loop:
                        response = self._arduino.readline().decode().replace('\r', '').replace('\n', '')

                        if response == "C0":
                            c = 0
                            i = 0
                        elif response == "C1":
                            c = 1
                            i = 0
                        elif response == "C2":
                            c = 2
                            i = 0
                        elif response == "C3":
                            c = 3
                            i = 0
                        elif response == "C4":
                            c = 4
                            i = 0
                        elif response == "C5":
                            c = 5
                            i = 0
                        elif response == "C6":
                            c = 6
                            i = 0
                        elif response == "C7":
                            c = 7
                            i = 0
                        elif response == "FINDEDATOS":
                            # This ADC data get cycle has reached end
                            do_loop = False

                            # Process raw ADC data
                            data = self._raw_data

                            # Convert raw ADC data to analog voltage
                            for c in range(0, len(data)):
                                for j in range(0, len(data[c])):
                                    data[c][j] = data[c][j] * self._VCC / 1023

                            # Delete DC component of AC sensors
                            for c in range(2, 5):

                                try:
                                    dc = np.mean(data[c])
                                except RuntimeWarning:
                                    dc = 0

                                for j in range(0, len(data[c])):
                                    data[c][j] -= dc

                            # Append data for DC sensors
                            self._adc_volts_data_ph = np.append(self._adc_volts_data_ph, data[0][0])
                            self._adc_volts_data_orp = np.append(self._adc_volts_data_orp, data[1][0])
                            self._adc_volts_data_sfp = np.append(self._adc_volts_data_sfp, data[5][0])
                            self._adc_volts_data_dfp = np.append(self._adc_volts_data_dfp, data[6][0])
                            self._adc_volts_data_tds = np.append(self._adc_volts_data_tds, data[7][0])

                            # For AC sensors, get the current rms value and save it
                            self._adc_volts_last_rms_voltage = self._get_rms(data[2])
                            self._adc_volts_last_rms_pump = self._get_rms(data[3])
                            self._adc_volts_last_rms_general = self._get_rms(data[4])

                        else:
                            try:
                                self._raw_data[c][i] = int(response)
                            except ValueError:
                                pass
                            i += 1

            except Exception:
                try:
                    self._arduino.close()
                except Exception:
                    pass

                # Try to restart ADC
                self._init_arduino()
                self._arduino.write(b's')  # Start ADC

    @staticmethod
    def _get_rms(data_vector, length=None):
        """
        This functions gets the RMS value of a given vector
        """
        result = 0

        if length is None:
            L = len(data_vector)
        else:
            L = length

        if L > 0:
            # create array of p, in_ch is samples, tm_w is window length
            a2 = np.power(data_vector, 2) / L
            v1 = np.array(a2[L - 1:])  # v1 = [p9, p10, ...]
            v2 = np.append([0], a2[0: len(a2) - L])  # v2 = [0,   p0, ...]
            acu = list(accumulate(a2[0: L - 1]))  # get initial accumulation (acu) of the window - 1
            v1[0] = v1[0] + acu[-1]  # rms element #1 will be at end of window and contains the accumulation
            rms_pw2 = list(accumulate(v1 - v2))
            rms = np.power(rms_pw2, 0.5)
            result = rms[0]

        return result

    def __del__(self):
        """
        Pool driver class destructor
        """
        # Cleanup
        try:
            self._arduino.close()
        except Exception:
            pass

        try:
            GPIO.cleanup()
            pass
        except Exception:
            pass

    def set_state(self, actuator, state):
        """
        This function set the state of a given actuator
        """
        if actuator == cfg.FILTER_PUMP:
            GPIO.output(self._PIN_PUMP_FILTER, state)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.FILTER_PUMP, state)
        elif actuator == cfg.BLEACH_PUMP:
            GPIO.output(self._PIN_PUMP_BLEACH, state)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.BLEACH_PUMP, state)
        elif actuator == cfg.ACID_PUMP:
            GPIO.output(self._PIN_PUMP_ACID, state)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.ACID_PUMP, state)
        elif actuator == cfg.AUX_OUT:
            GPIO.output(self._PIN_AUX_OUT, state)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.AUX_OUT, state)
        elif actuator == cfg.FILL_VALVE:
            GPIO.output(self._PIN_FILL_VALVE, state)
            logging.log(logging.DEBUG, strings.LOG_DRIVER_ACTUATOR_SET, cfg.FILL_VALVE, state)
        else:
            raise UnknownActuatorException

    def get_temperature(self):
        """ This method return the current temperature sensor information """
        temperature = None
        sensor_file = None
        try:
            sensor_file = open(self._TEMP_SENSOR, 'r')
            text = sensor_file.read()
            sensor_file.close()
            sensor_file = None
            second_line = text.split("\n")[1]
            temp_data = second_line.split(" ")[9]
            temperature = float(float(temp_data[2:]) / 1000)
        except Exception:
            if sensor_file is not None:
                try:
                    sensor_file.close()
                except Exception:
                    pass

        return temperature
