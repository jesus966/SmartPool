import logging

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from src.database.models import User
from src.driver import driver
from src.strings_constants import strings


class driverApi(Resource):
    """
    This class represent an API for driver data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_DRIVER, user.user_name)

        driver_data = {"last_ph_voltage": driver.last_ph_voltage,
                       "last_orp_voltage": driver.last_orp_voltage,
                       "last_tds_voltage": driver.last_tds_voltage,
                       "last_sand_pressure_voltage": driver.last_sand_pressure_voltage,
                       "last_diatoms_pressure_voltage": driver.last_diatoms_pressure_voltage}

        return jsonify(driver_data)

