#!/bin/bash
export ENV_FILE_LOCATION=/home/pi/SmartPool/src/.env
export PYTHONPATH=$PYTHONPATH:/home/pi/SmartPool
./python3 /home/pi/SmartPool/src/__main__.py --log_level=DEBUG --log_file="/home/pi/SmartPool/SmartPool.log"