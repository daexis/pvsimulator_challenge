import os
import time

from meter.Meter import Meter


def main():
    """
    Initializes consumer's meter and starts meter simulator.
    :return:
    """
    BROKER_HOST = os.environ.get('BROKER_HOST', 'rabbitmq')
    BROKER_PORT = os.environ.get('BROKER_PORT', '5672')
    BROKER_QUEUE = os.environ.get('BROKER_QUEUE', 'meter_simulator')
    BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'guest')
    BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'guest')
    PV_MIN = int(os.environ.get('PV_MIN', 0))
    PV_MAX = int(os.environ.get('PV_MAX', 9000))
    ITERATION = int(os.environ.get('ITERATION', 60))
    LOGFILE = os.environ.get('LOGFILE', './log/meter.log')
    ENVIRONMENT_PV = os.environ.get('ENVIRONMENT_PV', 'DEV')
    DELIMITER = os.environ.get('DELIMITER', ';')

    meter = Meter(BROKER_HOST, BROKER_PORT, BROKER_QUEUE, BROKER_USERNAME,
                  BROKER_PASSWORD, PV_MIN, PV_MAX, ITERATION,
                  LOGFILE, ENVIRONMENT_PV, DELIMITER)
    meter.start()


if __name__ == '__main__':
    main()
