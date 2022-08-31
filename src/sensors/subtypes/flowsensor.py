import datetime

import pymongo
from bson.codec_options import CodecOptions
from flask import jsonify

from src.config.pool import poolcfg
from src.database import timezone
from src.database.db import db
from src.database.models import FlowData
from src.models import Timer
from src.sensors import Sensor

from pymongo import errors

class FlowSensor(Sensor):
    """
    This is a special class that has additional methods to measure water flow
    """

    _counter = 0
    k_factor = poolcfg.pool_flow_k_factor
    _flow_timer = None
    _start_increment = datetime.datetime.now()
    _flow_save_timer = None
    flow = 0
    daily_volume = 0
    day = datetime.datetime.now().day

    def __init__(self, sensor_type, max_value=None, min_value=None, callback=None):
        """
        Constructor of the class
        """

        super().__init__(sensor_type, max_value, min_value, callback)
        self.load_from_db()
        poolcfg.pool_flow_k_factor_cb = self._update_config
        _flow_timer = Timer(self._get_flow)
        _flow_timer.start()
        _flow_save_timer = Timer(self._save_flow)
        _flow_save_timer.start()

    def _update_config(self):
        """
        This method updates current config from poolcfg.
        """
        self.k_factor = poolcfg.pool_flow_k_factor

    def _save_flow(self):
        """
        This method is called every second to save flow if needed
        """
        if self.flow != 0:
            self.save_to_db()

        if self.day != datetime.datetime.now().day:
            # If there is a new day, reset statistics
            self.daily_volume = 0
            self.save_to_db()
            self.day = datetime.datetime.now().day

    def _get_flow(self):
        """
        This method is called every second to update statistics
        """
        # Get current time and calculate time between calls
        last_increment = datetime.datetime.now()
        delta_t = last_increment - self._start_increment
        self._start_increment = last_increment

        if delta_t.total_seconds() <= 0:
            delta_t = datetime.timedelta(seconds=1)

        # Check the frequency between calls

        frequency = self._counter / delta_t.total_seconds()
        # Get flow in liters per minute
        self.flow = (frequency / self.k_factor) * (1 / (60 * delta_t.total_seconds()))

        self.daily_volume += self.flow / 1000  # Volume in m3
        self._counter = 0

    def add_tick(self):
        """
        This method adds a tick to the flow counter
        """

        self._counter += 1

    def load_from_db(self):
        """
        This method search's for the lastes record in the database
        and loads its data.

        Returns:

        """

        # Search into the database for the most recent record

        try:
            col = db.get_db().get_collection("flow_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            record = col.find().limit(1).sort("datetime", pymongo.DESCENDING)[0]

            if self.day != record["datetime"].day:
                self.daily_volume = 0
            else:
                self.daily_volume = record["daily_volume"]

        except IndexError:
            pass

    def save_to_db(self):
        """
        This method saves the current sensor into the database
        """
        try:
            # Create a new SensorData object in database and save all the data
            col = db.get_db().get_collection("flow_data").with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone))
            flowdb = FlowData()
            flowdb.datetime = timezone.localize(datetime.datetime.now())
            flowdb.daily_volume = self.daily_volume

            # If there is a new day save a new record, if not update last record
            if self.day != datetime.datetime.now().day:
                flowdb.save()
            else:
                col.replace_one({}, flowdb.to_mongo(), upsert=True)
        except errors.PyMongoError:
            pass

    def to_json(self):
        """
        This method converts all the info contained in the sensor to JSON
        """
        sensor_data = {"datetime": timezone.localize(datetime.datetime.now()), "flow": self.flow,
                       "daily_volume": self.daily_volume}
        return jsonify(sensor_data)
