
# Command line argument strings_constants
APP_DESCRIPTION = 'SmartPool server daemon app'  # App description for the command line
ARG_LOG_FILE_HELP = 'Path to the log file'
ARG_LOG_FILE_DEF = 'SmartPool.log'
ARG_LOG_LEVEL_HELP = 'Sets the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
ARG_LOG_LEVEL_DEF = 'INFO'

# Error Strings
ERR_LOGFILE_NOT_FOUND = 'Incorrect LOG file specified in path, skipping log...'
ERR_ENVAR_NOT_SET = 'The environment variable ENV_FILE_LOCATION is not set. Exiting...'
ERR_ENVAR_FILE_NOT_FOUND = 'Could not open the ENV file specified. Exiting...'

# Algorithm state strings_constants
STR_STATE_WAITING_DAILY_CYCLE = "waiting for filter"
STR_STATE_FILTERING = "filtering"
STR_STATE_WAITING_FOR_FILL = "waiting for sensor to detect no water"
STR_STATE_FILLING = "filling pool"
STR_STATE_WAITING_FOR_NIGHT = "waiting for night"
STR_STATE_WAITING_FOR_DAY = "waiting for day"

# Log strings_constants
LOG_STARTED = 'Logging started.'
LOG_STARTING_API = 'Starting API...'
LOG_START_DB = 'Database starting...'
LOG_USER_LOGIN = 'Login attempt for user: %s'
LOG_LOGIN_FAILED = 'Login attempt FAILED for user: %s'
LOG_LOGIN_SUCCESS = 'Login attempt SUCCEEDED for user: %s'
LOG_LOGIN_NOT_EXISTS = 'User %s does not exists in the database!'
LOG_LOGIN_NOT_ADMIN = 'User %s tried to access an unauthorized endpoint (he is not admin)'

LOG_CHEM_DEC_VALUE = 'Level of %s tank has been decreased by %.3f. Current tank level: %.3f'
LOG_CHEM_LOADED = 'Last level value loaded from %s tank is %.3f l.'
LOG_CHEM_LOAD_FAIL = 'No previous level records for %s tank found. Treating tank as if it is full.'
LOG_CHEM_INSTANTIATED = 'Tank of %s created. Max capacity in liters is %.3f l.'
LOG_CHEM_REFILLED = 'Refilled %s tank.'
LOG_CHEM_SET_VALUE = 'Level of the chemical tank of %s has been set to %.3f'

LOG_SENSOR_INSTANTIATED = 'New %s created.'
LOG_SENSOR_NEW_VALID_VALUE = 'New VALID %s sensor value added.'
LOG_SENSOR_NEW_INVALID_VALUE = 'New INVALID %s sensor value.'

LOG_ACTUATOR_INSTANTIATED = 'New %s actuator created.'

LOG_DRIVER_INSTANTIATED = 'Pool board initialized successfully.'
LOG_DRIVER_ACTUATOR_SET = 'Actuator %s set to a new state: %s'

LOG_ACT_CTR_INSTANTIATED = 'Actuator control class initialized.'
LOG_ACT_CTR_STATE_CHANGED = 'Changed state of the %s to %s. Source: %s'
LOG_ACT_CTR_NOT_ALLOWED = 'Request to change %s to an %s state automatically FAILED. We are on manual control.'
LOG_ACT_CTR_AUTOMATIC = "Automatic request"
LOG_ACT_CTR_MANUAL = "MANUAL request"
LOG_ACT_CTR_LOAD_FAIL = "No previous records of actuators (of the current date, at least) found. Clearing statistics."
LOG_ACT_CTR_LOADED = "Loaded previous records of statistical data for the actuators for today."
LOG_ACT_CTR_NOT_LOADED = "Previous records of statistical data for the actuators found, but it isn't for today. " \
                         "Clearing statistics..."
LOG_ACT_CTR_ESTOP = "EMERGENCY STOP requested. Pumps stopped."
LOG_ACT_CTR_RESUME = "EMERGENCY STOP ended, resuming normal operation..."

LOG_CFG_INSTANTIATED = "Pool dynamic config class initialized."
LOG_CFG_LOADED = "Loaded previous data for dynamic config."
LOG_CFG_NOT_LOADED = "Previous data for dynamic config not found in database. Loading defaults."

LOG_DFILT_INSTANTIATED = "Daily filtering algorithm class initialized."
LOG_DFILT_LOADED = "Loaded previous data for daily filtering algorithm."
LOG_DFILT_NOT_LOADED = "Previous data for daily filtering algorithm not found in database. Loading defaults."
LOG_DFILT_STATE_CHANGE = "Filter algorithm state changed to %s..."

LOG_FILTER_INSTANTIATED = "Class %s initialized."
LOG_FILTER_LOADED = "Loaded previous data of %s."
LOG_FILTER_NOT_LOADED = "Previous data for %s not found in database. Loading defaults."

LOG_CHEMICALS_INSTANTIATED = "Chemicals algorithm class initialized."
LOG_CHEMICALS_LOADED = "Loaded previous data for chemicals algorithm."
LOG_CHEMICALS_NOT_LOADED = "Previous data for chemicals algorithm not found in database. Loading defaults."
LOG_CHEMICALS_ORP_ERROR = "New chemical injection cycle of ORP started. Measured ORP error to correct: %.3f mV. Total " \
                          "bleach injection seconds: %ds. "
LOG_CHEMICALS_PH_ERROR = "New chemical injection cycle of PH started. Measured PH error to correct: %.3f. Total " \
                          "acid injection seconds: %ds. "
LOG_CHEMICALS_NO_ORP_ERROR = "New chemical injection cycle of ORP started, but there are no error to correct."
LOG_CHEMICALS_NO_PH_ERROR = "New chemical injection cycle of PH started, but there are no error to correct."

LOG_LEVELS_INSTANTIATED = "Water level algorithm class initialized."
LOG_LEVELS_LOADED = "Loaded previous data for water level algorithm."
LOG_LEVELS_NOT_LOADED = "Previous data for water level algorithm not found in database. Loading defaults."
LOG_LEVELS_STATE = "Water level control algorithm changed state to %s..."

LOG_LIGHTS_INSTANTIATED = "Lights algorithm class initialized."
LOG_LIGHTS_LOADED = "Loaded previous data for lights algorithm."
LOG_LIGHTS_NOT_LOADED = "Previous data for lights algorithm not found in database. Loading defaults."
LOG_LIGHTS_NET_ERROR = "NET ERROR SENDING LIGHT COMMAND: %s."
LOG_LIGHTS_STATE = "Light control algorithm changed state to %s..."

LOG_WATER_INSTANTIATED = "Water class initialized."
LOG_WATER_LOADED = "Loaded previous data of water."
LOG_WATER_NOT_LOADED = "Previous data of water not found in database. Loading defaults."

LOG_API_SENSOR = "API: User %s requested info from %s."
LOG_API_ACTUATOR = "API: User %s requested info of %s."
LOG_API_FILTER = "API: User %s requested info of filter algorithm."
LOG_API_CHEMICALS = "API: User %s requested info of chemical algorithm."
LOG_API_TANK = "API: User %s requested info of chemical tanks."
LOG_API_DRIVER = "API: User %s requested info of driver data."
LOG_API_TANK_SET = "API: User %s requested set of chemical tanks."
LOG_API_LEVEL = "API: User %s requested info of level control algorithm."
LOG_API_LIGHT = "API: User %s requested info of light control algorithm."
LOG_API_MOON = "API: User %s requested info of current moon phase."
LOG_API_LIGHT_SET = "API: User %s sets lights."
LOG_API_ACTUATOR_ALL = "API: User %s requested info of all actuators."
LOG_API_ACTUATOR_SET = "API: User %s sets state of %s."
LOG_API_CONFIG = "API: User %s requested view pool config."
LOG_API_WATER = "API: User %s requested view water data."
LOG_API_SUMMARY = "API: User %s requested a summary for all sensor data."
LOG_API_WATER_SET = "API: User %s sets water paremeters."

