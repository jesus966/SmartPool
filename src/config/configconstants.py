import src.strings_constants.strings as strings
"""
This file has configuration constants that aren't allowed to change without specifically change its value here.
Therefore, these configurations constants are 'hardwired' in normal operation of the app.
"""
TOKEN_EXPIRE_DAYS = 10  # Days that the Token used in user login expires
TIMEZONE = "Europe/Madrid"

''' Constants related to the driver '''
# Actuators
FILTER_PUMP = "filter pump"
BLEACH_PUMP = "bleach pump"
ACID_PUMP = "acid pump"
AUX_OUT = "aux output"
FILL_VALVE = "fill valve"

# Sensors
LIGHT_SENSOR = "light sensor"
TEMP_SENSOR = "temperature sensor"
PUMP_SENSOR = "filter pump intensity sensor"
GENERAL_SENSOR = "general intensity sensor"
VOLTAGE_SENSOR = "mains voltage sensor"
PH_SENSOR = "ph sensor"
ORP_SENSOR = "orp sensor"
TDS_SENSOR = "tds sensor"
SAND_PRESSURE_SENSOR = "sand pressure sensor"
DIATOMS_PRESSURE_SENSOR = "diatoms pressure sensor"
FLOW_SENSOR = "fill water flow sensor"
WATER_LEVEL_SENSOR = "water level sensor"
EMERGENCY_STOP_SENSOR = "emergency stop sensor"

''' Constants related to actuators '''
ESTOP_CAUSE_SENSOR = "emergency stop sensor"

''' Maximum and minimum value for poolconfig variables '''
SENSOR_REFRESH_MAX_MINUTES = 20
SENSOR_REFRESH_MIN_MINUTES = 1
TANK_SEC_DECREASE_VALUE_LITERS = 4/3600

''' Default poolconfig constants '''
SENSOR_REFRESH_MINUTES = 15
DAILY_FILTER_ALLOWED_HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
POOL_HYDRODYNAMIC_FACTOR = 15
POOL_RECIRCULATION_PERIOD = 4
POOL_ORP_MV_SETPOINT = 650
POOL_PH_SETPOINT = 7.4
POOL_ORP_AUTO_INJECTION_DISABLED = False
POOL_PH_AUTO_INJECTION_DISABLED = False
POOL_MAX_ORP_DAILY_SECONDS = 3600
POOL_MAX_PH_DAILY_SECONDS = 3600
POOL_FLOW_K_FACTOR = 7.5
POOL_FILL_START_LEVEL = 1
POOL_FILL_END_LEVEL = 3
POOL_MAX_DAILY_WATER_VOLUME_M3 = 2
POOL_FILL_VOLUME_BETWEEN_CHECKS = 0.5
POOL_FILL_SECONDS_WAIT = 30
POOL_AUTO_LIGHTS_ON = True
POOL_AUTO_LIGHTS_ON_COMMAND_SEQUENCE = [[3, 2 * 60 * 60]]

''' Constants for filter class '''
DIATOMS_TYPE = "diatom filter"
SAND_TYPE = "sand filter"

''' Constants related to daily filtering '''
STATE_WAITING_DAILY_CYCLE = strings.STR_STATE_WAITING_DAILY_CYCLE
STATE_FILTERING = strings.STR_STATE_FILTERING

''' Constants related to automatic water fill '''
STATE_WAITING_FOR_FILL = strings.STR_STATE_WAITING_FOR_FILL
STATE_FILLING = strings.STR_STATE_FILLING

''' Constants related to light control '''
STATE_WAITING_FOR_NIGHT = strings.STR_STATE_WAITING_FOR_NIGHT
STATE_WAITING_FOR_DAY = strings.STR_STATE_WAITING_FOR_DAY

