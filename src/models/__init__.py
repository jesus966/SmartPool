from src.models.chemicaltank import ChemicalTank
import src.config.configconstants as cfg
from src.models.timer import Timer

# Instantiate bleach and acid tanks
bleachTank = ChemicalTank("bleach", 25)
acidTank = ChemicalTank("acid", 25)

from src.models.filter import Filter

# Instantiate filters
diatomsFilter = Filter(cfg.DIATOMS_TYPE)
sandFilter = Filter(cfg.SAND_TYPE)

from src.models.actuatorcontrol import ActuatorControl

# Instantiate ActuatorControl
actuators = ActuatorControl()

from src.models.water import Water

# Instantiate Water class
water = Water()