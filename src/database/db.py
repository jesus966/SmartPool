import logging
import src.strings_constants.strings as Strings
from flask_mongoengine import MongoEngine

db = MongoEngine()


def initialize_db(app):
    # Initialize mongoDB
    logging.log(logging.DEBUG, Strings.LOG_START_DB)
    db.init_app(app)
