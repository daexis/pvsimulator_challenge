import pika
from meter.Meter import Meter
import unittest
import logging


class testMeter(unittest.TestCase):
    """
    Class for testing Meter.
    """
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
        """
        Test connection to broker.
        :return:
        """
        try:
            Meter._connect_broker(self)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_publishing(self):
        """
        Test publishing meter's value to broker.
        :return:
        """
        try:
            channel = Meter._connect_broker(self)
            Meter._publish_meter_to_broker(self, channel, "1234")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_generating(self):
        """
        Test generating meter's value.
        :return:
        """
        try:
            Meter._generate_meter(self, 2)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_morning_strgt_meter(self):
        """
        Test generating morning's meter's value.
        :return:
        """
        try:
            Meter._morning_strgt_meter(self, 1)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_evening_strgt_meter(self):
        """
        Test generating evening's meter's value.
        :return:
        """
        try:
            Meter._evening_strgt_meter(self, 1)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_get_fraction_time(self):
        """
        Test getting fraction time.
        :return:
        """
        try:
            Meter._get_fraction_time(self, 1, 2, 3)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()
