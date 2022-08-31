import logging

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import FieldDoesNotExist

from src.api.resources.errors import UnauthorizedError, SchemaValidationError, InternalServerError
from src.config.pool import poolcfg
from src.database.models import User
from src.strings_constants import strings


class poolConfigApi(Resource):
    """
    This class represent an API for pool config class
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_CONFIG, user.user_name)

        config = {"sensor_refresh_minutes": poolcfg.sensor_refresh_minutes,
                  "daily_filter_allowed_hours": poolcfg.daily_filter_allowed_hours,
                  "pool_hydrodynamic_factor": poolcfg.pool_hydrodynamic_factor,
                  "pool_recirculation_period": poolcfg.pool_recirculation_period,
                  "pool_orp_mv_setpoint": poolcfg.pool_orp_mv_setpoint,
                  "pool_ph_setpoint": poolcfg.pool_ph_setpoint,
                  "pool_orp_auto_injection_disabled": poolcfg.pool_orp_auto_injection_disabled,
                  "pool_ph_auto_injection_disabled": poolcfg.pool_ph_auto_injection_disabled,
                  "pool_max_orp_daily_seconds": poolcfg.pool_max_orp_daily_seconds,
                  "pool_max_ph_daily_seconds": poolcfg.pool_max_ph_daily_seconds,
                  "pool_flow_k_factor": poolcfg.pool_flow_k_factor,
                  "pool_fill_start_level": poolcfg.pool_fill_start_level,
                  "pool_fill_end_level": poolcfg.pool_fill_end_level,
                  "pool_max_daily_water_volume_m3": poolcfg.pool_max_daily_water_volume_m3,
                  "pool_fill_volume_between_checks": poolcfg.pool_fill_volume_between_checks,
                  "pool_fill_seconds_wait": poolcfg.pool_fill_seconds_wait,
                  "pool_auto_lights_on": poolcfg.pool_auto_lights_on,
                  "pool_auto_lights_on_command_sequence": poolcfg.pool_auto_lights_on_command_sequence
                  }

        return jsonify(config)

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        The PUT method modifies all current poolconfig data.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change pool config

            # Get JSON and parse it
            body = request.get_json()
            config_data = body.get('modify_data')

            if config_data is None:
                raise FieldDoesNotExist

            sensor_refresh_minutes = config_data["sensor_refresh_minutes"]
            daily_filter_allowed_hours = config_data["daily_filter_allowed_hours"]
            pool_hydrodynamic_factor = config_data["pool_hydrodynamic_factor"]
            pool_recirculation_period = config_data["pool_recirculation_period"]
            pool_orp_mv_setpoint = config_data["pool_orp_mv_setpoint"]
            pool_ph_setpoint = config_data["pool_ph_setpoint"]
            pool_orp_auto_injection_disabled = config_data["pool_orp_auto_injection_disabled"]
            pool_ph_auto_injection_disabled = config_data["pool_ph_auto_injection_disabled"]
            pool_max_orp_daily_seconds = config_data["pool_max_orp_daily_seconds"]
            pool_max_ph_daily_seconds = config_data["pool_max_ph_daily_seconds"]
            pool_flow_k_factor = config_data["pool_flow_k_factor"]
            pool_fill_start_level = config_data["pool_fill_start_level"]
            pool_fill_end_level = config_data["pool_fill_end_level"]
            pool_max_daily_water_volume_m3 = config_data["pool_max_daily_water_volume_m3"]
            pool_fill_volume_between_checks = config_data["pool_fill_volume_between_checks"]
            pool_fill_seconds_wait = config_data["pool_fill_seconds_wait"]
            pool_auto_lights_on = config_data["pool_auto_lights_on"]
            pool_auto_lights_on_command_sequence = config_data["pool_auto_lights_on_command_sequence"]

            # Set new data
            poolcfg.set_sensor_refresh_minutes(sensor_refresh_minutes)
            poolcfg.set_daily_filter_allowed_hours(daily_filter_allowed_hours)
            poolcfg.set_pool_hydrodynamic_factor(pool_hydrodynamic_factor)
            poolcfg.set_pool_recirculation_period(pool_recirculation_period)
            poolcfg.set_pool_orp_mv_setpoint(pool_orp_mv_setpoint)
            poolcfg.set_pool_ph_setpoint(pool_ph_setpoint)
            poolcfg.set_pool_orp_auto_injection_disabled(pool_orp_auto_injection_disabled)
            poolcfg.set_pool_ph_auto_injection_disabled(pool_ph_auto_injection_disabled)
            poolcfg.set_pool_max_orp_daily_seconds(pool_max_orp_daily_seconds)
            poolcfg.set_pool_max_ph_daily_seconds(pool_max_ph_daily_seconds)
            poolcfg.set_pool_flow_k_factor(pool_flow_k_factor)
            poolcfg.set_pool_fill_start_level(pool_fill_start_level)
            poolcfg.set_pool_fill_end_level(pool_fill_end_level)
            poolcfg.set_pool_max_daily_water_volume_m3(pool_max_daily_water_volume_m3)
            poolcfg.set_pool_fill_volume_between_checks(pool_fill_volume_between_checks)
            poolcfg.set_pool_fill_seconds_wait(pool_fill_seconds_wait)
            poolcfg.set_pool_auto_lights_on(pool_auto_lights_on)
            poolcfg.set_pool_auto_lights_on_command_sequence(pool_auto_lights_on_command_sequence)

            # Return modify OK
            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

        # Requires Auth

    @jwt_required()
    def patch(self):
        """
        The PATCH method modifies all certain poolconfig data.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change pool config

            # Get JSON and parse it
            body = request.get_json()
            config_data = body.get('modify_data')

            if config_data is None:
                raise FieldDoesNotExist

            try:
                sensor_refresh_minutes = config_data["sensor_refresh_minutes"]
                poolcfg.set_sensor_refresh_minutes(sensor_refresh_minutes)
            except KeyError:
                pass

            try:
                daily_filter_allowed_hours = config_data["daily_filter_allowed_hours"]
                poolcfg.set_daily_filter_allowed_hours(daily_filter_allowed_hours)
            except KeyError:
                pass

            try:
                pool_hydrodynamic_factor = config_data["pool_hydrodynamic_factor"]
                poolcfg.set_pool_hydrodynamic_factor(pool_hydrodynamic_factor)
            except KeyError:
                pass

            try:
                pool_recirculation_period = config_data["pool_recirculation_period"]
                poolcfg.set_pool_recirculation_period(pool_recirculation_period)
            except KeyError:
                pass

            try:
                pool_orp_mv_setpoint = config_data["pool_orp_mv_setpoint"]
                poolcfg.set_pool_orp_mv_setpoint(pool_orp_mv_setpoint)
            except KeyError:
                pass

            try:
                pool_ph_setpoint = config_data["pool_ph_setpoint"]
                poolcfg.set_pool_ph_setpoint(pool_ph_setpoint)
            except KeyError:
                pass

            try:
                pool_orp_auto_injection_disabled = config_data["pool_orp_auto_injection_disabled"]
                poolcfg.set_pool_orp_auto_injection_disabled(pool_orp_auto_injection_disabled)
            except KeyError:
                pass

            try:
                pool_ph_auto_injection_disabled = config_data["pool_ph_auto_injection_disabled"]
                poolcfg.set_pool_ph_auto_injection_disabled(pool_ph_auto_injection_disabled)
            except KeyError:
                pass

            try:
                pool_max_orp_daily_seconds = config_data["pool_max_orp_daily_seconds"]
                poolcfg.set_pool_max_orp_daily_seconds(pool_max_orp_daily_seconds)
            except KeyError:
                pass

            try:
                pool_max_ph_daily_seconds = config_data["pool_max_ph_daily_seconds"]
                poolcfg.set_pool_max_ph_daily_seconds(pool_max_ph_daily_seconds)
            except KeyError:
                pass

            try:
                pool_flow_k_factor = config_data["pool_flow_k_factor"]
                poolcfg.set_pool_flow_k_factor(pool_flow_k_factor)
            except KeyError:
                pass

            try:
                pool_fill_start_level = config_data["pool_fill_start_level"]
                poolcfg.set_pool_fill_start_level(pool_fill_start_level)
            except KeyError:
                pass

            try:
                pool_fill_end_level = config_data["pool_fill_end_level"]
                poolcfg.set_pool_fill_end_level(pool_fill_end_level)
            except KeyError:
                pass

            try:
                pool_max_daily_water_volume_m3 = config_data["pool_max_daily_water_volume_m3"]
                poolcfg.set_pool_max_daily_water_volume_m3(pool_max_daily_water_volume_m3)
            except KeyError:
                pass

            try:
                pool_fill_volume_between_checks = config_data["pool_fill_volume_between_checks"]
                poolcfg.set_pool_fill_volume_between_checks(pool_fill_volume_between_checks)
            except KeyError:
                pass

            try:
                pool_fill_seconds_wait = config_data["pool_fill_seconds_wait"]
                poolcfg.set_pool_fill_seconds_wait(pool_fill_seconds_wait)
            except KeyError:
                pass

            try:
                pool_auto_lights_on = config_data["pool_auto_lights_on"]
                poolcfg.set_pool_auto_lights_on(pool_auto_lights_on)
            except KeyError:
                pass

            try:
                pool_auto_lights_on_command_sequence = config_data["pool_auto_lights_on_command_sequence"]
                poolcfg.set_pool_auto_lights_on_command_sequence(pool_auto_lights_on_command_sequence)
            except KeyError:
                pass

            # Return modify OK
            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

    @staticmethod
    def check_if_is_admin():
        # Check if the current user is an admin
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)

        if user.is_admin is not True:
            # This user isn't an admin user, raise Exception
            logging.log(logging.INFO, strings.LOG_LOGIN_NOT_ADMIN, user.user_name)
            raise UnauthorizedError
