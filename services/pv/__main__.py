import logging
import os
import time
from datetime import datetime
from functools import wraps

from pv.PV import Pv


def main():
    """
    Initializes PV and starts PV simulator.
    :return:
    """
    BROKER_HOST = os.environ.get('BROKER_HOST', 'rabbitmq')
    BROKER_PORT = os.environ.get('BROKER_PORT', '5672')
    BROKER_QUEUE = os.environ.get('BROKER_QUEUE', 'meter_simulator')
    BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'guest')
    BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'guest')
    PV_MIN = int(os.environ.get('PV_MIN', 0))
    PV_MAX = int(os.environ.get('PV_MAX', 9000))
    OUTPUT_FILE = os.environ.get('OUTPUT_FILE', 'output.csv')
    DELIMITER = os.environ.get('DELIMITER', ';')
    LOGFILE = os.environ.get('LOGFILE', './log/pv.log')
    ENVIRONMENT_PV = os.environ.get('ENVIRONMENT_PV', 'DEV')
    MAX_EXECUTE_TIME = int(os.environ.get('MAX_EXECUTE_TIME', 60))
    EXECUTE_TIME_LOG = os.environ.get('EXECUTE_TIME_LOG', './log/execute_time.log')

    pv = Pv(BROKER_HOST, BROKER_PORT, BROKER_QUEUE, BROKER_USERNAME,
            BROKER_PASSWORD, PV_MIN, PV_MAX, OUTPUT_FILE,
            DELIMITER, LOGFILE, ENVIRONMENT_PV, MAX_EXECUTE_TIME, EXECUTE_TIME_LOG)
    pv.start()


if __name__ == '__main__':
    main()
