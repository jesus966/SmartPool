from src.actuators.actuator import Actuator
import src.config.configconstants as cfg

# Instantiate all actuators
filterPump = Actuator(cfg.FILTER_PUMP)
bleachPump = Actuator(cfg.BLEACH_PUMP)
acidPump = Actuator(cfg.ACID_PUMP)
auxOut = Actuator(cfg.AUX_OUT)
fillValve = Actuator(cfg.FILL_VALVE)