import pika
from meter.Meter import Meter
import unittest
import logging


class testMeter(unittest.TestCase, Meter):
    """
    Class for testing Meter.
    """
    _environment_pv = "TEST"
    _broker_host = "rabbitmq"
    _broker_port = '5672'
    _broker_queue = "meter_simulator_test"
    _broker_username = "guest"
    _broker_password = "guest"
    _pv_min = 0
    _pv_max = 9000
    _time_iter = 60
    _logfile = "./log/tests.log"
    _max_consume = 14

    _credentials = pika.PlainCredentials(_broker_username, _broker_password)

    def test_connection(self):
        """
        Test connection to broker.
        :return:
        """
        try:
            self._connect_broker()
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_publishing(self):
        """
        Test publishing meter's value to broker.
        :return:
        """
        try:
            channel = self._connect_broker()
            self._publish_meter_to_broker(channel, "1234")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_generating(self):
        """
        Test generating meter's value.
        :return:
        """
        try:
            self._generate_meter(2)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_morning_strgt_meter(self):
        assert self._morning_strgt_meter(0) == 0

    def test_evening_strgt_meter(self):
        assert self._evening_strgt_meter(1) == 0

    def test_get_fraction_time(self):
        assert self._get_fraction_time(0) == 0
        assert self._get_fraction_time(24) == 1


if __name__ == "__main__":
    unittest.main()
