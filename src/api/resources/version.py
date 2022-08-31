from flask import Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from mongoengine.errors import FieldDoesNotExist, \
    NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError

from .errors import SchemaValidationError


class VersionApi(Resource):
    @jwt_required()
    def get(self):
        return Response("{\"version\":1.0}", mimetype="application/json", status=200)