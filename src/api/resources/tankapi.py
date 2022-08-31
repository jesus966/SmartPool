import logging

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from src.database.models import User
from src.models import bleachTank, acidTank
from src.strings_constants import strings
from src.api.resources.errors import UnauthorizedError, InternalServerError, SchemaValidationError, BadRequestError

class tankApi(Resource):
    """
    This class represent an API for tank data
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_TANK, user.user_name)

        tank_data = {"bleach_tank_level": bleachTank.current_liters,
                     "acid_tank_level": acidTank.current_liters}

        return jsonify(tank_data)

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method set the state of a water tank
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_TANK_SET, user.user_name)

            # Get JSON and parse it
            body = request.get_json()
            acid_tank_level = body.get('acid_tank_level')
            bleach_tank_level = body.get('bleach_tank_level')

            if acid_tank_level is not None:
                acidTank.set_value(acid_tank_level)

            if bleach_tank_level is not None:
                bleachTank.set_value(bleach_tank_level)

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