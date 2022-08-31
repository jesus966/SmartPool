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
from src.algorithms import dailyfiltering, chemicals, levelControl, lightControl
from src.strings_constants import strings


class algFilterApi(Resource):
    """
    Class that implements API method that represents the filter algorithm
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics of the algorithm
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_FILTER, user.user_name)

            return_data = {"state": dailyfiltering.state, "total_daily_seconds": dailyfiltering.total_daily_seconds,
                           "total_daily_seconds_remaining": dailyfiltering.total_daily_seconds_remaining}

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


class algChemApi(Resource):
    """
    Class that implements API method that represents the chemical algorithm
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics of the algorithm
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_CHEMICALS, user.user_name)

            return_data = {"algorithm_cycle_seconds": chemicals.algorithm_cycle_seconds,
                           "algorithm_orp_injected_seconds": chemicals.algorithm_orp_injected_seconds,
                           "algorithm_ph_injected_seconds": chemicals.algorithm_ph_injected_seconds,
                           "total_orp_daily_seconds": chemicals.total_orp_daily_seconds,
                           "total_ph_daily_seconds": chemicals.total_ph_daily_seconds
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


class algFillApi(Resource):
    """
    Class that implements API method that represents the level control algorithm
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics of the algorithm
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_LEVEL, user.user_name)

            return_data = {
                "state": levelControl.state,
                "daily_filled_volume": levelControl.daily_filled_volume,
                "start_volume": levelControl.start_volume
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


class algLightsApi(Resource):
    """
    Class that implements API method that represents the light control algorithm
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        try:
            """
            This method send the current state and statistics of the algorithm
            """
            # Get the name of the user that has requested data
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_LIGHT, user.user_name)

            return_data = {
                "state": lightControl.state,
                "lights_are_on": lightControl.lights_are_on
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
        This method set the lights
        """
        try:
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_LIGHT_SET, user.user_name)

            # Get JSON and parse it
            body = request.get_json()
            command = body.get('execute_command')

            if command is None:
                sequence = body.get('execute_sequence')

                if sequence is None:
                    raise FieldDoesNotExist

                lightControl.execute_command_sequence(sequence)

            else:
                lightControl.send_command(command)

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

