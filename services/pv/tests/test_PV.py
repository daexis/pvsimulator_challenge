from datetime import datetime

import pika
from pv.PV import Pv
import unittest
import logging


class testPv(unittest.TestCase, Pv):
    """
    Class for testing PV Simulator
    """
    _environment_pv = "TEST"
    _broker_host = "rabbitmq"
    _broker_port = "5672"
    _broker_queue = "meter_simulator_test"
    _broker_username = "guest"
    _broker_password = "guest"
    _output_file ="./log/output_test.csv"
    _delimiter =";"
    _pv_min = 0
    _pv_max = 9000
    _logfile ="./log/pv_log.log"
    _time_iter = 60
    _max_execute_time = 60
    _execute_time_log ="./log/execute_time_test.log"
    _pv_sunrise_start = 6
    _pv_sunrise_end = 8
    _pv_zenith = 14
    _pv_sundown_start = 20
    _pv_sundown_end = 21
    _pv_light_eff_lw = 0.1
    _pv_light_eff_std = 0.8125
    _pv_max_power = 9000

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

    def test_generating(self):
        """
        Test generating pv simulator's value.
        :return:
        """
        try:
            self._generate_pv_value(1,1)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_writing(self):
        """
        Test writing pv simulator's value to output file.
        :return:
        """
        try:
            data_record = {
                "timestamp": 1,
                "meter_value": "-1234",
                "pv_value": "1234",
                "sum": "0"
            }
            self._write_to_output(1, data_record, "DATA")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_get_value_from_broker(self):
        try:
            channel = self._connect_broker()
            self._get_value_from_broker(channel)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_parse_data_string(self):
        assert self._parse_data_string("1;1;1234") == [1, 1, 1234]

    def test_make_filename(self):
        assert self._make_filename(1) == "./log/output_test_day1.csv"

    def test_make_plot_filename(self):
        assert self._make_plot_filename(1) == "./log/output_test_day1.png"

    def test_get_fraction_time(self):
        assert self._get_fraction_time(0) == 0
        assert self._get_fraction_time(24) == 1

    def test_morning_strgt(self):
        assert self._morning_strgt(0) == -2700.0

    def test_evening_strgt(self):
        assert self._evening_strgt(1) == 144000.0

    def test_parabola(self):
        assert self._parabola(0) == -17800.0

if __name__ == "__main__":
    unittest.main()
