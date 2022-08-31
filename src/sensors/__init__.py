from src.sensors.sensor import Sensor
import src.config.configconstants as cfg

# Instantiate all sensors
lightSensor = Sensor(cfg.LIGHT_SENSOR)
temperatureSensor = Sensor(cfg.TEMP_SENSOR)
pumpSensor = Sensor(cfg.PUMP_SENSOR)
generalSensor = Sensor(cfg.GENERAL_SENSOR)
voltageSensor = Sensor(cfg.VOLTAGE_SENSOR)
phSensor = Sensor(cfg.PH_SENSOR, min_value=6.9, max_value=8.2)
orpSensor = Sensor(cfg.ORP_SENSOR, min_value=0, max_value=1000)
tdsSensor = Sensor(cfg.TDS_SENSOR)
sandPressureSensor = Sensor(cfg.SAND_PRESSURE_SENSOR)
diatomsPressureSensor = Sensor(cfg.DIATOMS_PRESSURE_SENSOR)
waterLevelSensor_1 = Sensor(cfg.WATER_LEVEL_SENSOR)
waterLevelSensor_2 = Sensor(cfg.WATER_LEVEL_SENSOR)
waterLevelSensor_3 = Sensor(cfg.WATER_LEVEL_SENSOR)
waterLevelSensor_4 = Sensor(cfg.WATER_LEVEL_SENSOR)
waterLevelSensor_5 = Sensor(cfg.WATER_LEVEL_SENSOR)
waterLevelSensor_6 = Sensor(cfg.WATER_LEVEL_SENSOR)
emergencyStopSensor = Sensor(cfg.EMERGENCY_STOP_SENSOR)
