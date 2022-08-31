import datetime
import logging
import socket
import time

import pymongo

import src.strings_constants.strings as strings
from src.database import timezone
from src.database.db import db
from src.database.models import LightsAlgorithmData
from bson.codec_options import CodecOptions

from src.models import Timer
from src.sensors import lightSensor
import src.config.configconstants as cfg
from src.config.pool import poolcfg

from pymongo import errors

class Lights:
    """
    This is a class that implements the pool light control Algorithm
    """

    ''' LUMIPLUS protocol constants '''
    _HOST = '192.168.2.1'
    _PORT = 123

    # Control constants
    _COMMAND_SHUTDOWN = b'023080'

    # Colour constants
    _COMMAND_RED = b'023049'
    _COMMAND_GREEN = b'023051'
    _COMMAND_BLUE = b'023050'
    _COMMAND_WHITE = b'023060'
    _COMMAND_TURQUOISE = b'023055'
    _COMMAND_ORANGE = b'023053'
    _COMMAND_YELLOW = b'023058'
    _COMMAND_MID_BLUE = b'023054'
    _COMMAND_LOW_BLUE = b'023057'
    _COMMAND_HIGH_PINK = b'023052'
    _COMMAND_MED_PINK = b'023056'
    _COMMAND_LOW_PINK = b'023059'

    # Predefined sequences commands
    _COMMAND_SEQUENCE_ABRIL = b'023184'
    _COMMAND_SEQUENCE_PARADISE = b'023170'
    _COMMAND_SEQUENCE_TROPICAL = b'023179'
    _COMMAND_SEQUENCE_CANDY = b'023199'
    _COMMAND_SEQUENCE_IRIS = b'023248'
    _COMMAND_SEQUENCE_CAROLINE = b'023234'
    _COMMAND_SEQUENCE_ESTIVAL = b'023243'
    _COMMAND_SEQUENCE_ELEVEN = b'023135'

    # Speed change commands
    _COMMAND_SPEED_0 = b'023072'
    _COMMAND_SPEED_1 = b'023071'
    _COMMAND_SPEED_2 = b'023070'
    _COMMAND_SPEED_3 = b'023069'
    _COMMAND_SPEED_4 = b'023068'
    _COMMAND_SPEED_5 = b'023067'
    _COMMAND_SPEED_6 = b'023066'

    # Timing commands
    _COMMAND_TIMING_0 = b'023097'
    _COMMAND_TIMING_1 = b'023098'
    _COMMAND_TIMING_2 = b'023099'
    _COMMAND_TIMING_3 = b'023100'
    _COMMAND_TIMING_4 = b'023101'
    _COMMAND_TIMING_5 = b'023102'
    _COMMAND_TIMING_6 = b'023103'
    _COMMAND_TIMING_7 = b'023104'

    ''' Algorithm constants '''
    auto_lights_on = poolcfg.pool_auto_lights_on
    auto_lights_on_command_sequence = poolcfg.pool_auto_lights_on_command_sequence["sequence"]

    state = cfg.STATE_WAITING_FOR_NIGHT
    lights_are_on = False
    light_timer = None

    def __init__(self):
        logging.log(logging.INFO, strings.LOG_LIGHTS_INSTANTIATED)
        self.load_from_db()
        if self.auto_lights_on:
            if lightSensor.value:
                # Change state
                self.state = cfg.STATE_WAITING_FOR_NIGHT
                logging.log(logging.INFO, strings.LOG_LIGHTS_STATE, cfg.STATE_WAITING_FOR_NIGHT)
            else:
                self.state = cfg.STATE_WAITING_FOR_DAY
                logging.log(logging.INFO, strings.LOG_LIGHTS_STATE, cfg.STATE_WAITING_FOR_DAY)
        light_timer = Timer(self._light_algorithm)
        light_timer.start()

    def _light_algorithm(self):
        """
        This is called a fixed amount of time to execute the light control algorithm
        """
        if self.auto_lights_on:
            if self.state == cfg.STATE_WAITING_FOR_NIGHT:
                # Check if the light sensor indicates that there isn't light
                if not lightSensor.value:
                    # Change state
                    self.state = cfg.STATE_WAITING_FOR_DAY
                    logging.log(logging.INFO, strings.LOG_LIGHTS_STATE, cfg.STATE_WAITING_FOR_DAY)
                    # Execute command sequence
                    self.execute_command_sequence(self.auto_lights_on_command_sequence)
            elif self.state == cfg.STATE_WAITING_FOR_DAY:
                # Check if there is light on the sensor
                if lightSensor.value:
                    # Change state
                    self.state = cfg.STATE_WAITING_FOR_NIGHT
                    logging.log(logging.INFO, strings.LOG_LIGHTS_STATE, cfg.STATE_WAITING_FOR_NIGHT)

    def set_auto_command_sequence(self, sequence):
        """
        This method sets what sequence will be executed by the algorithm when its night
        """
        self.auto_lights_on_command_sequence = sequence
        self.save_to_db()

    def execute_command_sequence(self, sequence):
        """
        This method executes a given command sequence
        """
        # Iterate the sequence list
        for cmd_list in sequence:
            '''
            Each cmd_list is itself another list with two positions.
            First position is the light command number itself and
            second position is the duration of the command in seconds
            '''
            if cmd_list[1] <= 0:
                self.send_command(cmd_list[0])
            else:
                if self.send_command(cmd_list[0]):
                    if cmd_list[1] == 5 * 60:
                        self.send_command(28)
                    elif cmd_list[1] == 15 * 60:
                        self.send_command(29)
                    elif cmd_list[1] == 30 * 60:
                        self.send_command(30)
                    elif cmd_list[1] == 60 * 60:
                        self.send_command(31)
                    elif cmd_list[1] == 90 * 60:
                        self.send_command(32)
                    elif cmd_list[1] == 2 * 60 * 60:
                        self.send_command(33)
                    elif cmd_list[1] == 4 * 60 * 60:
                        self.send_command(34)
                    elif cmd_list[1] == 8 * 60 * 60:
                        self.send_command(35)
                    else:
                        time.sleep(cmd_list[1])

    def set_automatic_light_control(self, state: bool):
        """
        This method sets the state of the automatic light control algorithm
        """
        self.auto_lights_on = state
        self.save_to_db()

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("lights_algorithm_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]
            self.lights_are_on = record["lights_are_on"]
            logging.log(logging.INFO, strings.LOG_LIGHTS_LOADED)

        except IndexError:
            logging.log(logging.INFO, strings.LOG_LIGHTS_NOT_LOADED)

    def save_to_db(self):
        """
        This method saves data into the database.

        Returns:

        """
        try:
            col = db.get_db().get_collection("lights_algorithm_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))

            # Create a new object in database and save all the data
            lightsdb = LightsAlgorithmData()

            lightsdb.datetime = timezone.localize(datetime.datetime.now())
            lightsdb.lights_are_on = self.lights_are_on
            col.replace_one({}, lightsdb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass

    def send_command(self, command: int) -> bool:
        """
        This function sends a light command to the LUMIPLUS controller
        """
        # First, map the command with the corresponding LUMIPLUS command

        light_command = None

        if command == 0:
            light_command = self._COMMAND_SHUTDOWN
        elif command == 1:
            light_command = self._COMMAND_RED
        elif command == 2:
            light_command = self._COMMAND_GREEN
        elif command == 3:
            light_command = self._COMMAND_BLUE
        elif command == 4:
            light_command = self._COMMAND_WHITE
        elif command == 5:
            light_command = self._COMMAND_TURQUOISE
        elif command == 6:
            light_command = self._COMMAND_ORANGE
        elif command == 7:
            light_command = self._COMMAND_YELLOW
        elif command == 8:
            light_command = self._COMMAND_MID_BLUE
        elif command == 9:
            light_command = self._COMMAND_LOW_BLUE
        elif command == 10:
            light_command = self._COMMAND_HIGH_PINK
        elif command == 11:
            light_command = self._COMMAND_MED_PINK
        elif command == 12:
            light_command = self._COMMAND_LOW_PINK
        elif command == 13:
            light_command = self._COMMAND_SEQUENCE_ABRIL
        elif command == 14:
            light_command = self._COMMAND_SEQUENCE_PARADISE
        elif command == 15:
            light_command = self._COMMAND_SEQUENCE_TROPICAL
        elif command == 16:
            light_command = self._COMMAND_SEQUENCE_CANDY
        elif command == 17:
            light_command = self._COMMAND_SEQUENCE_IRIS
        elif command == 18:
            light_command = self._COMMAND_SEQUENCE_CAROLINE
        elif command == 19:
            light_command = self._COMMAND_SEQUENCE_ESTIVAL
        elif command == 20:
            light_command = self._COMMAND_SEQUENCE_ELEVEN
        elif command == 21:
            light_command = self._COMMAND_SPEED_0
        elif command == 22:
            light_command = self._COMMAND_SPEED_1
        elif command == 23:
            light_command = self._COMMAND_SPEED_2
        elif command == 24:
            light_command = self._COMMAND_SPEED_3
        elif command == 25:
            light_command = self._COMMAND_SPEED_4
        elif command == 26:
            light_command = self._COMMAND_SPEED_5
        elif command == 27:
            light_command = self._COMMAND_SPEED_6
        elif command == 28:
            light_command = self._COMMAND_TIMING_0
        elif command == 29:
            light_command = self._COMMAND_TIMING_1
        elif command == 30:
            light_command = self._COMMAND_TIMING_2
        elif command == 31:
            light_command = self._COMMAND_TIMING_3
        elif command == 32:
            light_command = self._COMMAND_TIMING_4
        elif command == 33:
            light_command = self._COMMAND_TIMING_5
        elif command == 34:
            light_command = self._COMMAND_TIMING_6
        elif command == 35:
            light_command = self._COMMAND_TIMING_7

        data_ok = False

        if light_command is not None:
            # Create socket and send command
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self._HOST, self._PORT))
                    s.sendall(light_command)  # Send the command
                    data = s.recv(1024)
                    # Check if received data is equal to sent data
                    if data == light_command:
                        data_ok = True
            except socket.error as e:
                logging.log(logging.ERROR, strings.LOG_LIGHTS_NET_ERROR, str(e))

        if 1 <= command <= 20 and data_ok:
            self.lights_are_on = True
            self.save_to_db()

        if command == 0 and data_ok:
            self.lights_are_on = False
            self.save_to_db()

        return data_ok
