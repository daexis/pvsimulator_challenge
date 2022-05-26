import pika
from meter.Meter import Meter
import unittest
import logging


class testMeter(unittest.TestCase):
    _broker_host = 'rabbitmq'
    _broker_port = '5672'
    _broker_queue = 'meter_simulator_test'
    _broker_username = 'guest'
    _broker_password = 'guest'
    _credentials = pika.PlainCredentials(_broker_username, _broker_password)
    _logfile = "./log/tests.log"
    _pv_min = 0
    _pv_max = 9000
    _pv_delay = 5
    _environment_pv = "TEST"

    def test_connection(self):
        try:
            Meter._connect_broker(self)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_publishing(self):
        try:
            channel = Meter._connect_broker(self)
            Meter._publish_meter_to_broker(self, channel, "1234")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_generating(self):
        try:
            Meter._generate_meter(self)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
