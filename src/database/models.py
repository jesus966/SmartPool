from flask_bcrypt import generate_password_hash, check_password_hash

from .db import db


class User(db.Document):
    """
    User model for the database, a user consist of a username, an email,
    a password and a variable for determining if the user is an admin or not.
    """
    user_name = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True, min_length=6)
    is_admin = db.BooleanField(required=True)

    def hash_password(self):
        """
        This method hashes the password for storing it in a more secure way that
        in plain text.
        """
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        """
        This method compare the specified password hash with the stored password hash,
        for determining if the user has logged on correctly.
        """
        return check_password_hash(self.password, password)


class SensorData(db.Document):
    """
    This database model holds generic data applicable to all sensors.
    """

    '''
    Id and value of the sensor, in dict. There are several ids used as key for the dict:
        - "ph"
        - "orp"
        - "tds"
        - "temperature"
        - "pressure"
        - "voltage"
        - "intensity"
    '''
    id_value = db.DictField(required=True)
    '''
    Stores if the sensor data is OK or not
    '''
    is_ok = db.BooleanField(required=True)
    '''
    Field for saving the date and time of this sensor data
    '''
    datetime = db.DateTimeField(required=True)


class ChemicalTankData(db.Document):
    """
    This database model holds generic data applicable to chemical tanks.
    """

    '''
    Type of the thank, there are two types:
        - "bleach"
        - "acid"
    '''
    tank_type = db.StringField(required=True)
    '''
    Stores if the current value in liters of the tank
    '''
    current_liters = db.FloatField(required=True)
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)


class ActuatorData(db.Document):
    """
    This database model holds generic data applicable to all actuators.
    """

    '''
    Field that stores what type of actuator is
    '''
    actuator_id = db.StringField(required=True)
    '''
    Stores if the sensor data is OK or not
    '''
    state = db.BooleanField(required=True)
    '''
    Field for saving the date and time of this actuator data
    '''
    datetime = db.DateTimeField(required=True)


class ActuatorControlData(db.Document):
    """
    This database model holds statistical data of all the actuators.
    """

    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field that stores if we are on emergency stop
    '''
    in_emergency_stop = db.BooleanField(required=True)

    '''
    Field that stores what its the cause of the emergency stop
    '''
    emergency_stop_cause = db.StringField(required=True)

    '''
    Field that stores if the pumps are in manual or automatic mode.
    '''
    pump_automatic_control = db.BooleanField(required=True)

    '''
    Field that stores if the fill valve are in manual or automatic mode.
    '''
    valve_automatic_control = db.BooleanField(required=True)

    '''
    Field that stores the teoric state of the filter pump.
    '''
    filter_pump_teoric_state = db.BooleanField(required=True)

    '''
    Field that stores the state of the bleach pump.
    '''
    bleach_pump_state = db.BooleanField(required=True)

    '''
    Field that stores the state of the acid pump.
    '''
    acid_pump_state = db.BooleanField(required=True)

    '''
    Field that stores the state of the aux out.
    '''
    aux_out_state = db.BooleanField(required=True)

    '''
    Field that stores the state of the fill valve.
    '''
    fill_valve_state = db.BooleanField(required=True)

    '''
    Field that stores the REAL number of seconds that the filter pump has been on.
    '''
    filter_pump_on_real_seconds = db.IntField(required=True)

    '''
    Field that stores the TOTAL number of seconds that theoretically the filter pump has been on.
    '''
    filter_pump_on_total_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the filter pump has been on in auto mode.
    '''
    filter_pump_on_auto_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the filter pump has been on in manual mode.
    '''
    filter_pump_on_manual_seconds = db.IntField(required=True)

    '''
    Field that stores the TOTAL number of seconds that theoretically the bleach pump has been on.
    '''
    bleach_pump_on_total_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the bleach pump has been on in auto mode.
    '''
    bleach_pump_on_auto_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the bleach pump has been on in manual mode.
    '''
    bleach_pump_on_manual_seconds = db.IntField(required=True)

    '''
    Field that stores the TOTAL number of seconds that theoretically the acid pump has been on.
    '''
    acid_pump_on_total_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the acid pump has been on in auto mode.
    '''
    acid_pump_on_auto_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the acid pump has been on in manual mode.
    '''
    acid_pump_on_manual_seconds = db.IntField(required=True)

    '''
    Field that stores the TOTAL number of seconds that theoretically the aux out has been on.
    '''
    aux_out_on_total_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the aux out has been on in auto mode.
    '''
    aux_out_on_auto_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the aux out has been on in manual mode.
    '''
    aux_out_on_manual_seconds = db.IntField(required=True)

    '''
    Field that stores the TOTAL number of seconds that theoretically the fill valve has been on.
    '''
    fill_valve_on_total_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the fill valve has been on in auto mode.
    '''
    fill_valve_on_auto_seconds = db.IntField(required=True)
    '''
    Field that stores the number of seconds that the fill valve has been on in manual mode.
    '''
    fill_valve_on_manual_seconds = db.IntField(required=True)


class PoolConfigData(db.Document):
    """
    This database model holds dynamic config data for the pool.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving sensor refresh time
    '''
    sensor_refresh_minutes = db.IntField(required=True)

    '''
    Field for saving the allowed hours of filtering
    '''
    daily_filter_allowed_hours = db.ListField(required=True)

    '''
    Field for saving the pool hydrodynamic factor
    '''
    pool_hydrodynamic_factor = db.IntField(required=True)

    '''
    Field for saving the pool recirculation period
    '''
    pool_recirculation_period = db.FloatField(required=True)

    '''
    Field for saving the pool orp setpoint
    '''
    pool_orp_mv_setpoint = db.FloatField(required=True)

    '''
    Field for saving the pool ph setpoint
    '''
    pool_ph_setpoint = db.FloatField(required=True)

    '''
    Field for saving if the orp injection algorithm is disabled
    '''
    pool_orp_auto_injection_disabled = db.BooleanField(required=True)

    '''
    Field for saving if the ph injection algorithm is disabled
    '''
    pool_ph_auto_injection_disabled = db.BooleanField(required=True)

    '''
    Field for saving max daily orp injection seconds
    '''
    pool_max_orp_daily_seconds = db.IntField(required=True)

    '''
    Field for saving max daily orp injection seconds
    '''
    pool_max_ph_daily_seconds = db.IntField(required=True)

    '''
    Field for saving the K calibration factor for flow meter
    '''
    pool_flow_k_factor = db.FloatField(required=True)

    '''
    Field for saving in which level we will star filling the pool
    '''
    pool_fill_start_level = db.IntField(required=True)

    '''
    Field for saving in which level we will end filling the pool
    '''
    pool_fill_end_level = db.IntField(required=True)

    '''
    Field for saving what is the max daily level in m3 of water to be filled
    '''
    pool_max_daily_water_volume_m3 = db.FloatField(required=True)

    '''
    Field for saving what volume will fill before check if we are done filling
    '''
    pool_fill_volume_between_checks = db.FloatField(required=True)

    '''
    Field for saving the number of seconds between fill checks
    '''
    pool_fill_seconds_wait = db.IntField(required=True)

    '''
    Field for saving if the light algorithm is on
    '''
    pool_auto_lights_on = db.BooleanField(required=True)

    '''
    Field for saving the auto light command sequence
    '''
    pool_auto_lights_on_command_sequence = db.DictField(required=True)

    '''
    Field for saving what volume will fill before check if we are done filling
    '''
    pool_fill_volume_between_checks = db.FloatField(required=True)

class FilterAlgorithmData(db.Document):
    """
    This database model holds  data for the filter algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the total max daily seconds of filtering
    '''
    total_daily_seconds = db.IntField(required=True)

    '''
    Field for saving the total daily seconds remaining of filtering
    '''
    total_daily_seconds_remaining = db.IntField(required=True)


class FilterData(db.Document):
    """
    This database model holds  data for the filter algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the type of filter
    '''
    type = db.StringField(required=True)

    '''
    Field for saving the pressure of the filter
    '''
    pressure = db.FloatField(required=True)


class ChemicalsAlgorithmData(db.Document):
    """
    This database model holds  data for the chemicals algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the current algorithm cycle seconds
    '''
    algorithm_cycle_seconds = db.IntField(required=True)

    '''
    Field for saving the current algorithm orp pending injected seconds
    '''
    algorithm_orp_injected_seconds = db.IntField(required=True)

    '''
    Field for saving the current algorithm ph pending injected seconds
    '''
    algorithm_ph_injected_seconds = db.IntField(required=True)

    '''
    Field for saving the total orp injected seconds today
    '''
    total_orp_daily_seconds = db.IntField(required=True)

    '''
    Field for saving the total ph injected seconds today
    '''
    total_ph_daily_seconds = db.IntField(required=True)


class LevelAlgorithmData(db.Document):
    """
    This database model holds  data for the chemicals algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the current state of the algorithm
    '''
    state = db.StringField(required=True)

    '''
    Field for saving the daily automatic filled volume
    '''
    daily_filled_volume = db.FloatField(required=True)

    '''
    Field for saving the algorithm start water volume
    '''
    start_volume = db.FloatField(required=True)


class LightsAlgorithmData(db.Document):
    """
    This database model holds  data for the chemicals algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving if the lights are currently on
    '''
    lights_are_on = db.BooleanField(required=True)


class FlowData(db.Document):
    """
    This database model holds data of the fill flow of the pool
    """

    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the daily volume
    '''
    daily_volume = db.FloatField(required=True)


class WaterData(db.Document):
    """
    This database model holds  data for the chemicals algorithm.
    """
    '''
    Field for saving the date and time of this data
    '''
    datetime = db.DateTimeField(required=True)

    '''
    Field for saving the temperature data
    '''
    temperature = db.FloatField(required=False)

    '''
    Field for saving the orp data
    '''
    orp = db.FloatField(required=False)

    '''
    Field for saving the ph data
    '''
    ph = db.FloatField(required=False)

    '''
    Field for saving the tds data
    '''
    tds = db.FloatField(required=False)

    '''
    Field for saving water levels
    '''
    levels = db.DictField(required=False)

    '''
    Field for saving total alkalinity
    '''
    alkalinity = db.FloatField(required=False)

    '''
    Field for saving total hardness
    '''
    hardness = db.FloatField(required=False)

    '''
    Field for saving lsi
    '''
    LSI = db.FloatField(required=False)

    '''
    Field for saving cya
    '''
    cya = db.FloatField(required=False)

    '''
    Field for saving if the data is valid
    '''
    valid = db.BooleanField(required=False)
