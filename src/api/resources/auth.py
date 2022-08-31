import datetime
import logging

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, \
    NotUniqueError, DoesNotExist

import src.strings_constants.strings as Strings
from src.database.models import User
from .errors import SchemaValidationError, InternalServerError, \
    UnauthorizedError, UserNotExistsError, UserNameAlreadyExistsError, EmptyBodyError

import src.config.configconstants as DefaultConfig


class UsersApi(Resource):
    """
    Class that implements API method to get a list with all the current users in the system
    """

    # Requires Auth
    @jwt_required()
    def get(self):
        """
        The GET method returns a JSON with all the users that are in the database and their basic
        information.
        """
        try:
            # First, check what user is logged on the system
            user_id = get_jwt_identity()
            user = User.objects.get(id=user_id)

            if user.is_admin is not True:
                # This user isn't an admin user, raise Exception
                logging.log(logging.INFO, Strings.LOG_LOGIN_NOT_ADMIN, user.user_name)
                raise UnauthorizedError

            # Create a dict table with all the users in the database
            user_table = []

            for user in User.objects.all():
                current_user = dict()
                current_user["user_name"] = user.user_name
                current_user["email"] = user.email
                current_user["is_admin"] = user.is_admin
                user_table.append(current_user)

            # Convert dict table to JSON and send the data
            json_output = jsonify({"Users": user_table})

            return json_output

        except FieldDoesNotExist:
            raise SchemaValidationError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError


class SignupApi(Resource):
    """
    Class that implements API method to register a new user
    """

    # Requires Auth
    @jwt_required()
    def post(self):
        """
        The POST method creates a new user, but only a previous user with admin rights is allowed to add
        new users.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to add a new user

            # Get JSON and parse it
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            uid = user.id

            # Return registration OK
            return {'id': str(uid)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise UserNameAlreadyExistsError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def put(self):
        """
        The PUT method updates the user data, using full representation. But only a previous user
        with admin rights is allowed to update users.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to update a user

            # First, get current username to modify from JSON
            body = request.get_json()
            user = User.objects.get(user_name=body.get('modify_user'))

            # Now, get the new user data
            user_data = body.get('modify_data')

            # Change user data and update
            user.user_name = user_data["user_name"]
            user.email = user_data["email"]
            user.password = user_data["password"]
            user.is_admin = user_data["is_admin"]
            user.hash_password()
            user.save()
            uid = user.id

            # Return update OK
            return {'id': str(uid)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except KeyError:
            raise SchemaValidationError
        except NotUniqueError:
            raise UserNameAlreadyExistsError
        except DoesNotExist:
            raise UserNotExistsError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def patch(self):
        """
        The PATCH method updates the user data, without full representation. Only a previous user
        with admin rights is allowed to update users.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to update a user

            # First, get current username to modify from JSON
            body = request.get_json()
            user = User.objects.get(user_name=body.get('modify_user'))

            # Now, get the new user data
            user_data = body.get('modify_data')

            # Change user data and update, ignore data fields that are empty, and thus not changed
            try:
                user.user_name = user_data["user_name"]
            except KeyError:
                pass

            try:
                user.email = user_data["email"]
            except KeyError:
                pass

            try:
                user.password = user_data["password"]
                user.hash_password()
            except KeyError:
                pass

            try:
                user.is_admin = user_data["is_admin"]
            except KeyError:
                pass

            user.save()
            uid = user.id

            # Return update OK
            return {'id': str(uid)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise UserNameAlreadyExistsError
        except DoesNotExist:
            raise UserNotExistsError
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

    # Requires Auth
    @jwt_required()
    def delete(self):
        """
        The DELETE method deletes a user. Only a previous user with admin rights is allowed to delete users.
        """
        try:
            # First, check what user is logged on the system
            self.check_if_is_admin()

            # Is an admin, so it's OK to delete a user

            # Get username
            user_name = request.args.get('user')

            # Delete user
            User.objects.get(user_name=user_name).delete()

            # Return OK
            return '', 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise UserNameAlreadyExistsError
        except DoesNotExist:
            raise UserNotExistsError
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
            logging.log(logging.INFO, Strings.LOG_LOGIN_NOT_ADMIN, user.user_name)
            raise UnauthorizedError


class LoginApi(Resource):
    """
    Class that implements user LOGIN in API
    """

    def post(self):
        try:
            # Get JSON and parse it
            body = request.get_json()

            # Check username and password
            try:
                user = User.objects.get(user_name=body.get('user_name'))
            except DoesNotExist:
                logging.log(logging.INFO, Strings.LOG_LOGIN_NOT_EXISTS, body.get('user_name'))
                raise UnauthorizedError

            authorized = user.check_password(body.get('password'))

            logging.log(logging.INFO, Strings.LOG_USER_LOGIN, body.get('user_name'))

            if not authorized:
                # Password check failed
                logging.log(logging.INFO, Strings.LOG_LOGIN_FAILED, body.get('user_name'))
                raise UnauthorizedError

            logging.log(logging.INFO, Strings.LOG_LOGIN_SUCCESS, body.get('user_name'))

            # Login OK, send token
            expires = datetime.timedelta(days=DefaultConfig.TOKEN_EXPIRE_DAYS)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)

            response = {
                "token": access_token,
                "user_name": user.user_name,
                "email": user.email,
                "is_admin": user.is_admin
            }

            return response, 200
        except UnauthorizedError:
            raise UnauthorizedError
        except AttributeError:
            raise EmptyBodyError
        except Exception:
            raise InternalServerError
