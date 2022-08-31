import logging

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from src.database.models import User
from src.models import water
from src.strings_constants import strings
from src.api.resources.errors import UnauthorizedError, InternalServerError, SchemaValidationError, BadRequestError
from mongoengine import FieldDoesNotExist
from json import JSONDecodeError


class waterApi(Resource):
    """
    This class represent an API for water class
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        # Get the name of the user that has requested data
        user_id = get_jwt_identity()
        user = User.objects.get(id=user_id)
        logging.log(logging.INFO, strings.LOG_API_WATER, user.user_name)

        water_data = {"temperature": water.temperature, "orp": water.orp, "ph": water.ph,
                      "tds": water.tds, "valid": water.valid,
                      "levels": [water.levels[0], water.levels[1], water.levels[2],
                                 water.levels[3], water.levels[4], water.levels[5]],
                      "alkalinity": water.alkalinity, "hardness": water.hardness, "LSI": water.LSI,
                      "cya": water.cya}

        return jsonify(water_data)

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        This method sets all the data of water class
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_WATER_SET, user.user_name)

            # Get JSON and parse it
            body = request.get_json()

            if body is None:
                raise FieldDoesNotExist

            alkalinity = body.get('alkalinity')
            hardness = body.get('hardness')
            cya = body.get('cya')

            if alkalinity is None or hardness is None or cya is None:
                raise FieldDoesNotExist

            water.alkalinity = alkalinity
            water.hardness = hardness
            water.cya = cya
            water.save_to_db()

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

    # Requires Auth
    @jwt_required()
    def patch(self):
        """
        This method set some data of water class
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to change actuator state
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)
            logging.log(logging.INFO, strings.LOG_API_WATER_SET, user.user_name)

            # Get JSON and parse it
            body = request.get_json()

            if body is None:
                raise FieldDoesNotExist

            alkalinity = body.get('alkalinity')
            hardness = body.get('hardness')
            cya = body.get('cya')

            if alkalinity is not None:
                water.alkalinity = alkalinity

            if hardness is not None:
                water.hardness = hardness

            if cya is not None:
                water.cya = cya

            water.save_to_db()

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
