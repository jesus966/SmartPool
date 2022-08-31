class InternalServerError(Exception):
    pass


class SchemaValidationError(Exception):
    pass


class UserNotExistsError(Exception):
    pass


class UserNameAlreadyExistsError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class EmptyBodyError(Exception):
    pass


class NoAuthorizationError(Exception):
    pass


class ExpiredSignatureError(Exception):
    pass


class BadRequestError(Exception):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "UserNotExistsError": {
        "message": "The given user doesn't exists",
        "status": 400
    },
    "UserNameAlreadyExistsError": {
        "message": "The given user name already exists",
        "status": 400
    },
    "EmptyBodyError": {
        "message": "Didn't receive any JSON data on the request BODY",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    },
    "NoAuthorizationError": {
        "message": "Authorization required",
        "status": 401
    },
    "ExpiredSignatureError": {
        "message": "Authorization required, token has expired",
        "status": 401
    },
    "BadRequestError": {
        "message": "Bad request",
        "status": 400
    }
}
