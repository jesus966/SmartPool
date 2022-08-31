import logging
from json import JSONDecodeError

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from mongoengine import FieldDoesNotExist

import src.config.configconstants as cfg
from src.api.resources.errors import UnauthorizedError, InternalServerError, SchemaValidationError, BadRequestError
from src.database.models import User
from src.models import actuators
from src.strings_constants import strings


class actSummaryApi(Resource):
    """
    Class that implements API method that send a summary of all actuators data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for all actuators
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_ALL, user.user_name)

            # Send current data
            return_data = {"pump_automatic_control": actuators.PUMP_AUTOMATIC_CONTROL,
                           "valve_automatic_control": actuators.VALVE_AUTOMATIC_CONTROL,
                           "filter_pump_real_state": actuators.FILTER_PUMP_REAL_STATE,
                           "filter_pump_teoric_state": actuators.FILTER_PUMP_TEORIC_STATE,
                           "filter_pump_on_real_seconds": actuators.FILTER_PUMP_ON_REAL_SECONDS,
                           "filter_pump_on_total_seconds": actuators.FILTER_PUMP_ON_TOTAL_SECONDS,
                           "filter_pump_on_auto_seconds": actuators.FILTER_PUMP_ON_AUTO_SECONDS,
                           "filter_pump_on_manual_seconds": actuators.FILTER_PUMP_ON_MANUAL_SECONDS,
                           "filter_pump_seconds_since_last_on": actuators.FILTER_PUMP_SEC_SINCE_LAST_ON,
                           "bleach_pump_teoric_state": actuators.BLEACH_PUMP_STATE,
                           "bleach_pump_on_total_seconds": actuators.BLEACH_PUMP_ON_TOTAL_SECONDS,
                           "bleach_pump_on_auto_seconds": actuators.BLEACH_PUMP_ON_AUTO_SECONDS,
                           "bleach_pump_on_manual_seconds": actuators.BLEACH_PUMP_ON_MANUAL_SECONDS,
                           "bleach_pump_seconds_since_last_on": actuators.BLEACH_PUMP_SEC_SINCE_LAST_ON,
                           "acid_pump_teoric_state": actuators.ACID_PUMP_STATE,
                           "acid_pump_on_total_seconds": actuators.ACID_PUMP_ON_TOTAL_SECONDS,
                           "acid_pump_on_auto_seconds": actuators.ACID_PUMP_ON_AUTO_SECONDS,
                           "acid_pump_on_manual_seconds": actuators.ACID_PUMP_ON_MANUAL_SECONDS,
                           "acid_pump_seconds_since_last_on": actuators.ACID_PUMP_SEC_SINCE_LAST_ON,
                           "fill_valve_teoric_state": actuators.FILL_VALVE_STATE,
                           "fill_valve_on_total_seconds": actuators.FILL_VALVE_ON_TOTAL_SECONDS,
                           "fill_valve_on_auto_seconds": actuators.FILL_VALVE_ON_AUTO_SECONDS,
                           "fill_valve_on_manual_seconds": actuators.FILL_VALVE_ON_MANUAL_SECONDS,
                           "aux_out_teoric_state": actuators.AUX_OUT_STATE,
                           "aux_out_on_total_seconds": actuators.AUX_OUT_ON_TOTAL_SECONDS,
                           "aux_out_on_auto_seconds": actuators.AUX_OUT_ON_AUTO_SECONDS,
                           "aux_out_on_manual_seconds": actuators.AUX_OUT_ON_MANUAL_SECONDS,
                           "aux_out_seconds_since_last_on": actuators.AUX_OUT_SEC_SINCE_LAST_ON,
                           "in_emergency_stop": actuators.IN_EMERGENCY_STOP,
                           "emergency_stop_cause": actuators.EMERGENCY_STOP_CAUSE}

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError


class actFilterApi(Resource):
    """
    Class that implements API method that represents the filter pump
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for the actuator
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR, user.user_name, cfg.FILTER_PUMP)

            # Send current data
            return_data = {"automatic_control": actuators.PUMP_AUTOMATIC_CONTROL,
                           "real_state": actuators.FILTER_PUMP_REAL_STATE,
                           "teoric_state": actuators.FILTER_PUMP_TEORIC_STATE,
                           "pump_on_real_seconds": actuators.FILTER_PUMP_ON_REAL_SECONDS,
                           "pump_on_total_seconds": actuators.FILTER_PUMP_ON_TOTAL_SECONDS,
                           "pump_on_auto_seconds": actuators.FILTER_PUMP_ON_AUTO_SECONDS,
                           "pump_on_manual_seconds": actuators.FILTER_PUMP_ON_MANUAL_SECONDS,
                           "seconds_since_last_on": actuators.FILTER_PUMP_SEC_SINCE_LAST_ON,
                           "in_emergency_stop": actuators.IN_EMERGENCY_STOP,
                           "emergency_stop_cause": actuators.EMERGENCY_STOP_CAUSE}

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of an actuator
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state

            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_SET, user.user_name, cfg.FILTER_PUMP)

            # Get JSON and parse it
            body = request.get_json()
            automatic_control = body.get('automatic_control')
            if automatic_control is None:
                raise FieldDoesNotExist
            if not automatic_control:
                state = body.get('actuator_state')
                if state is None:
                    raise FieldDoesNotExist
                actuators.setstate(cfg.FILTER_PUMP, state, automatic=False)
            else:
                actuators.PUMP_AUTOMATIC_CONTROL = automatic_control

            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
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


class actBleachApi(Resource):
    """
    Class that implements API method that represents the bleach pump
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for the actuator
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR, user.user_name, cfg.BLEACH_PUMP)

            # Send current data
            return_data = {"automatic_control": actuators.PUMP_AUTOMATIC_CONTROL,
                           "teoric_state": actuators.BLEACH_PUMP_STATE,
                           "pump_on_total_seconds": actuators.BLEACH_PUMP_ON_TOTAL_SECONDS,
                           "pump_on_auto_seconds": actuators.BLEACH_PUMP_ON_AUTO_SECONDS,
                           "pump_on_manual_seconds": actuators.BLEACH_PUMP_ON_MANUAL_SECONDS,
                           "seconds_since_last_on": actuators.BLEACH_PUMP_SEC_SINCE_LAST_ON,
                           "in_emergency_stop": actuators.IN_EMERGENCY_STOP,
                           "emergency_stop_cause": actuators.EMERGENCY_STOP_CAUSE}

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of an actuator
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_SET, user.user_name, cfg.BLEACH_PUMP)

            # Get JSON and parse it
            body = request.get_json()
            automatic_control = body.get('automatic_control')
            if automatic_control is None:
                raise FieldDoesNotExist

            if not automatic_control:
                state = body.get('actuator_state')
                if state is None:
                    raise FieldDoesNotExist
                actuators.setstate(cfg.BLEACH_PUMP, state, automatic=False)
            else:
                actuators.PUMP_AUTOMATIC_CONTROL = automatic_control

            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
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


class actAcidApi(Resource):
    """
    Class that implements API method that represents the acid pump
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for the actuator
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR, user.user_name, cfg.ACID_PUMP)

            # Send current data
            return_data = {"automatic_control": actuators.PUMP_AUTOMATIC_CONTROL,
                           "teoric_state": actuators.ACID_PUMP_STATE,
                           "pump_on_total_seconds": actuators.ACID_PUMP_ON_TOTAL_SECONDS,
                           "pump_on_auto_seconds": actuators.ACID_PUMP_ON_AUTO_SECONDS,
                           "pump_on_manual_seconds": actuators.ACID_PUMP_ON_MANUAL_SECONDS,
                           "seconds_since_last_on": actuators.ACID_PUMP_SEC_SINCE_LAST_ON,
                           "in_emergency_stop": actuators.IN_EMERGENCY_STOP,
                           "emergency_stop_cause": actuators.EMERGENCY_STOP_CAUSE}

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of an actuator
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_SET, user.user_name, cfg.ACID_PUMP)

            # Get JSON and parse it
            body = request.get_json()
            automatic_control = body.get('automatic_control')
            if automatic_control is None:
                raise FieldDoesNotExist
            if not automatic_control:
                state = body.get('actuator_state')
                if state is None:
                    raise FieldDoesNotExist
                actuators.setstate(cfg.ACID_PUMP, state, automatic=False)
            else:
                actuators.PUMP_AUTOMATIC_CONTROL = automatic_control

            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
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


class actFillValveApi(Resource):
    """
    Class that implements API method that represents the fill valve
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for the actuator
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR, user.user_name, cfg.FILL_VALVE)

            # Send current data
            return_data = {"automatic_control": actuators.VALVE_AUTOMATIC_CONTROL,
                           "teoric_state": actuators.FILL_VALVE_STATE,
                           "on_total_seconds": actuators.FILL_VALVE_ON_TOTAL_SECONDS,
                           "on_auto_seconds": actuators.FILL_VALVE_ON_AUTO_SECONDS,
                           "on_manual_seconds": actuators.FILL_VALVE_ON_MANUAL_SECONDS,
                           "seconds_since_last_on": actuators.FILL_VALVE_SEC_SINCE_LAST_ON
                           }

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of an actuator
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_SET, user.user_name, cfg.FILL_VALVE)

            # Get JSON and parse it
            body = request.get_json()
            automatic_control = body.get('automatic_control')

            if automatic_control is None:
                raise FieldDoesNotExist

            if not automatic_control:
                state = body.get('actuator_state')
                if state is None:
                    raise FieldDoesNotExist
                actuators.setstate(cfg.FILL_VALVE, state, automatic=False)
            else:
                actuators.VALVE_AUTOMATIC_CONTROL = automatic_control

            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
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


class actAuxApi(Resource):
    """
    Class that implements API method that represents the aux actuator
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics for the actuator
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR, user.user_name, cfg.AUX_OUT)

            # Send current data
            return_data = {"teoric_state": actuators.AUX_OUT_STATE,
                           "on_total_seconds": actuators.AUX_OUT_ON_TOTAL_SECONDS,
                           "on_auto_seconds": actuators.AUX_OUT_ON_AUTO_SECONDS,
                           "on_manual_seconds": actuators.AUX_OUT_ON_MANUAL_SECONDS,
                           "seconds_since_last_on": actuators.AUX_OUT_SEC_SINCE_LAST_ON
                           }

            return jsonify(return_data)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of an actuator
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_ACTUATOR_SET, user.user_name, cfg.AUX_OUT)

            # Get JSON and parse it
            body = request.get_json()
            state = body.get('actuator_state')

            if state is None:
                raise FieldDoesNotExist

            actuators.setstate(cfg.AUX_OUT, state, automatic=False)

            return "", 200

        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise SchemaValidationError
        except JSONDecodeError:
            raise BadRequestError
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
