import datetime
import logging

from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from mongoengine import DoesNotExist

import src.config.configconstants as cfg
from src.api.resources.errors import UserNotExistsError
from src.database import timezone
from src.database.models import User
from src.models import water
from src.sensors import phSensor, orpSensor, tdsSensor, temperatureSensor, diatomsPressureSensor, sandPressureSensor, \
    voltageSensor, generalSensor, pumpSensor, lightSensor, emergencyStopSensor, waterLevelSensor_1, \
    waterLevelSensor_2, waterLevelSensor_3, waterLevelSensor_4, waterLevelSensor_5, waterLevelSensor_6
from src.sensors.subtypes import flowSensor
from src.strings_constants import strings


class summaryApi(Resource):
    """
    Class that implements API method that returns a summary of all sensor data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_SUMMARY, user.user_name)
            summary = {phSensor.sensor_type:
                           {"datetime": phSensor.datetime, "value": phSensor.value, "is_ok": phSensor.is_ok},
                       orpSensor.sensor_type:
                           {"datetime": orpSensor.datetime, "value": orpSensor.value, "is_ok": orpSensor.is_ok},
                       temperatureSensor.sensor_type:
                           {"datetime": temperatureSensor.datetime, "value": temperatureSensor.value,
                            "is_ok": temperatureSensor.is_ok},
                       tdsSensor.sensor_type:
                           {"datetime": tdsSensor.datetime, "value": tdsSensor.value, "is_ok": tdsSensor.is_ok},
                       diatomsPressureSensor.sensor_type:
                           {"datetime": diatomsPressureSensor.datetime, "value": diatomsPressureSensor.value,
                            "is_ok": diatomsPressureSensor.is_ok},
                       sandPressureSensor.sensor_type:
                           {"datetime": sandPressureSensor.datetime, "value": sandPressureSensor.value,
                            "is_ok": sandPressureSensor.is_ok},
                       voltageSensor.sensor_type:
                           {"datetime": voltageSensor.datetime, "value": voltageSensor.value, "is_ok": voltageSensor.is_ok},
                       generalSensor.sensor_type:
                           {"datetime": generalSensor.datetime, "value": generalSensor.value, "is_ok": generalSensor.is_ok},
                       pumpSensor.sensor_type:
                           {"datetime": pumpSensor.datetime, "value": pumpSensor.value, "is_ok": pumpSensor.is_ok},
                       lightSensor.sensor_type:
                           {"datetime": lightSensor.datetime, "value": lightSensor.value, "is_ok": lightSensor.is_ok},
                       emergencyStopSensor.sensor_type:
                           {"datetime": emergencyStopSensor.datetime, "value": emergencyStopSensor.value,
                            "is_ok": emergencyStopSensor.is_ok},
                       waterLevelSensor_1.sensor_type:
                           {"datetime": timezone.localize(datetime.datetime.now()),
                            "levels": water.levels},
                       flowSensor.sensor_type:
                           {"datetime": timezone.localize(datetime.datetime.now()), "flow": flowSensor.flow,
                            "daily_volume": flowSensor.daily_volume}}

            return jsonify(summary)

        except DoesNotExist:
            raise UserNotExistsError


class phApi(Resource):
    """
    Class that implements API method to get PH data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.PH_SENSOR)
        return phSensor.to_json()


class orpApi(Resource):
    """
    Class that implements API method to get ORP data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.ORP_SENSOR)
        return orpSensor.to_json()


class tdsApi(Resource):
    """
    Class that implements API method to get TDS data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.TDS_SENSOR)
        return tdsSensor.to_json()


class tempApi(Resource):
    """
    Class that implements API method to get TEMP data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.TEMP_SENSOR)
        return temperatureSensor.to_json()


class diatApi(Resource):
    """
    Class that implements API method to get DIATOMS data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.DIATOMS_PRESSURE_SENSOR)
        return diatomsPressureSensor.to_json()


class sandApi(Resource):
    """
    Class that implements API method to get SAND data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.SAND_PRESSURE_SENSOR)
        return sandPressureSensor.to_json()


class voltsApi(Resource):
    """
    Class that implements API method to get VOLTAGE data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.VOLTAGE_SENSOR)
        return voltageSensor.to_json()


class genApi(Resource):
    """
    Class that implements API method to get GENERAL INTENSITY data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.GENERAL_SENSOR)
        return generalSensor.to_json()


class filterApi(Resource):
    """
    Class that implements API method to get FILTER INTENSITY data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.PUMP_SENSOR)
        return pumpSensor.to_json()


class lightApi(Resource):
    """
    Class that implements API method to get LIGHT data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.LIGHT_SENSOR)
        return lightSensor.to_json()


class eStopApi(Resource):
    """
    Class that implements API method to get EMERGENCY STOP data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.EMERGENCY_STOP_SENSOR)
        return emergencyStopSensor.to_json()


class flowApi(Resource):
    """
    Class that implements API method to get FLOW data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.FLOW_SENSOR)
        return flowSensor.to_json()


class waterLevelApi(Resource):
    """
    Class that implements API method to get EMERGENCY STOP data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_SENSOR, user.user_name, cfg.WATER_LEVEL_SENSOR)
        # Water level info json
        water_level = {"datetime": timezone.localize(datetime.datetime.now()),
                       "levels": [waterLevelSensor_1.value, waterLevelSensor_2.value, waterLevelSensor_3.value,
                                  waterLevelSensor_4.value, waterLevelSensor_5.value, waterLevelSensor_6.value]}
        return jsonify(water_level)
