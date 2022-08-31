import argparse
import logging

from flask import Flask
import src.strings_constants.strings as strings
import sys
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from src.api.resources import errors
from src.database.db import initialize_db

""" Main function of the SmartPool application
It parses the command line arguments, and initialize all the classes """

# Instantiate the parser
parser = argparse.ArgumentParser(description=strings.APP_DESCRIPTION)

# Log file path argument
parser.add_argument('--log_file', type=str,
                    help=strings.ARG_LOG_FILE_HELP,
                    default=strings.ARG_LOG_FILE_DEF)

# Log level argument
parser.add_argument('--log_level', type=str,
                    help=strings.ARG_LOG_LEVEL_HELP,
                    default=strings.ARG_LOG_LEVEL_DEF)

# Parse arguments
args = parser.parse_args()

# Switch to the appropriate LOG LEVEL
if args.log_level == 'DEBUG':
    level = logging.DEBUG
elif args.log_level == 'INFO':
    level = logging.INFO
elif args.log_level == 'WARNING':
    level = logging.WARNING
elif args.log_level == 'ERROR':
    level = logging.ERROR
elif args.log_level == 'CRITICAL':
    level = logging.CRITICAL
else:
    level = logging.INFO

# Turn on Logging
try:
    logging.basicConfig(filename=args.log_file,
                        level=level, format='%(asctime)s %(message)s')

    logging.log(logging.INFO, strings.LOG_STARTED)

except FileNotFoundError:
    # If the file path was incorrect, print it on the screen
    print(strings.ERR_LOGFILE_NOT_FOUND, file=sys.stderr)

logging.log(logging.DEBUG, strings.LOG_STARTING_API)

# Variable that stores Flask APP
app = Flask(__name__)

try:
    app.config.from_envvar('ENV_FILE_LOCATION')
except RuntimeError:
    # If the env var is not set, print error and exit
    print(strings.ERR_ENVAR_NOT_SET, file=sys.stderr)
    exit()
except FileNotFoundError:
    # If the ENV file cannot be found, print error and exit
    print(strings.ERR_ENVAR_FILE_NOT_FOUND, file=sys.stderr)
    exit()

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

initialize_db(app)
