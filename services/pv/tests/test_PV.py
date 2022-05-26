from datetime import datetime

import pika
from pv.PV import Pv
import unittest
import logging


class testPv(unittest.TestCase):
    _broker_host = 'rabbitmq'
    _broker_port = '5672'
    _broker_queue = 'meter_simulator_test'
    _broker_username = 'guest'
    _broker_password = 'guest'
    _credentials = pika.PlainCredentials(_broker_username, _broker_password)
    _logfile = "./log/tests.log"
    _output_file = "./log/test_output.csv"
    _pv_min = 0
    _pv_max = 9000
    _pv_delay = 5
    _delimiter = ";"
    _environment_pv = "TEST"

    def test_connection(self):
        try:
            Pv._connect_broker(self)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_generating(self):
        try:
            Pv._generate_pv_value(self)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_writing(self):
        try:
            data_record = {
                "timestampt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "meter_value": "1234",
                "pv_value": "1234",
                "sum": "2468"
            }
            Pv._write_to_output(self, data_record)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
