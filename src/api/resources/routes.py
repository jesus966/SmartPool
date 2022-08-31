from .actuators import actFilterApi, actBleachApi, actAcidApi, actFillValveApi, actAuxApi, actSummaryApi
from .algorithms import algFilterApi, algChemApi, algFillApi, algLightsApi
from .moon import moonApi
from .poolconfigapi import poolConfigApi
from .tankapi import tankApi
from .version import VersionApi
from .auth import LoginApi, SignupApi, UsersApi
from .sensors import phApi, orpApi, tdsApi, tempApi, diatApi, sandApi, voltsApi, genApi, filterApi, lightApi, eStopApi, \
    waterLevelApi, flowApi, summaryApi
from .waterapi import waterApi
from .driverapi import driverApi


def initialize_routes(api):
    """ This Function routes every API class with its endpoints """
    # Api version endpoint
    api.add_resource(VersionApi, '/api/version')

    # Login endpoints
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')
    api.add_resource(UsersApi, '/api/auth/users')

    # Algorithms endpoints
    api.add_resource(algFilterApi, '/api/algorithms/filter')
    api.add_resource(algFillApi, '/api/algorithms/level')
    api.add_resource(algChemApi, '/api/algorithms/chemicals')
    api.add_resource(algLightsApi, '/api/algorithms/lights')

    # Models endpoints
    api.add_resource(waterApi, '/api/pool/water')
    api.add_resource(tankApi, '/api/pool/tank')
    api.add_resource(moonApi, '/api/sky/moon')

    # Pool config endpoint
    api.add_resource(poolConfigApi, '/api/pool/config')

    # Pool driver endpoint
    api.add_resource(driverApi, '/api/pool/driver/voltages')

    # Sensors endpoints
    api.add_resource(summaryApi, '/api/sensors/summary')
    api.add_resource(phApi, '/api/sensors/ph')
    api.add_resource(orpApi, '/api/sensors/orp')
    api.add_resource(tdsApi, '/api/sensors/tds')
    api.add_resource(tempApi, '/api/sensors/temperature')
    api.add_resource(diatApi, '/api/sensors/pressure/diatoms')
    api.add_resource(sandApi, '/api/sensors/pressure/sand')
    api.add_resource(voltsApi, '/api/sensors/voltage')
    api.add_resource(genApi, '/api/sensors/pump/general')
    api.add_resource(filterApi, '/api/sensors/pump/filter')
    api.add_resource(lightApi, '/api/sensors/light')
    api.add_resource(eStopApi, '/api/sensors/emergency_stop')
    api.add_resource(waterLevelApi, '/api/sensors/water_level')
    api.add_resource(flowApi, '/api/sensors/flow')

    # Actuators endpoints
    api.add_resource(actSummaryApi, '/api/actuators')
    api.add_resource(actFilterApi, '/api/actuators/pump/filter')
    api.add_resource(actBleachApi, '/api/actuators/pump/bleach')
    api.add_resource(actAcidApi, '/api/actuators/pump/acid')
    api.add_resource(actFillValveApi, '/api/actuators/fill')
    api.add_resource(actAuxApi, '/api/actuators/aux')
