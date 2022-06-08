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
    TIME_ITER = int(os.environ.get('TIME_ITER', 60))
    EXECUTE_TIME_LOG = os.environ.get('EXECUTE_TIME_LOG',
                                      './log/execute_time.log')
    PV_SUNRISE_START = int(os.environ.get('PV_SUNRISE_START', 6))
    PV_SUNRISE_END = int(os.environ.get('PV_SUNRISE_END', 8))
    PV_ZENITH = int(os.environ.get('PV_ZENITH', 14))
    PV_SUNDOWN_START = int(os.environ.get('PV_SUNDOWN_START', 20))
    PV_SUNDOWN_END = int(os.environ.get('PV_SUNDOWN_END', 21))
    PV_LIGHT_EFF_LW = float(os.environ.get('PV_LIGHT_EFF_LW', 0.1))
    PV_LIGHT_EFF_STD = float(os.environ.get('PV_LIGHT_EFF_STD', 0.8125))
    PV_MAX_POWER = int(os.environ.get('PV_MAX_POWER', 4000))

    pv = Pv(BROKER_HOST, BROKER_PORT, BROKER_QUEUE, BROKER_USERNAME,
            BROKER_PASSWORD, PV_MIN, PV_MAX, OUTPUT_FILE,
            DELIMITER, LOGFILE, ENVIRONMENT_PV, MAX_EXECUTE_TIME, TIME_ITER,
            EXECUTE_TIME_LOG, PV_SUNRISE_START, PV_SUNRISE_END, PV_ZENITH,
            PV_SUNDOWN_START, PV_SUNDOWN_END, PV_LIGHT_EFF_LW, PV_LIGHT_EFF_STD,
            PV_MAX_POWER)
    pv.start()


if __name__ == '__main__':
    main()
