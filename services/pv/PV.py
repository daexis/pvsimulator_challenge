import csv
import logging
import os
from datetime import datetime
from random import randint
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import pika


class Pv:
    """
    Class receiving consumer's meter value from a broker, generating PV value,
    writing to a file and makes plot of output data.
    Should provide broker's host, port, queue, username, password.
    """

    def __init__(self, broker_host: str, broker_port: int, broker_queue: str,
                 broker_username: str,
                 broker_password: str,
                 pv_min: int, pv_max: int,
                 output_file: str, delimiter: str, logfile: str,
                 environment_pv: str, max_execute_time: int, time_iter: int,
                 execute_time_log: str, pv_sunrise_start: int,
                 pv_sunrise_end: int, pv_zenith: int, pv_sundown_start: int,
                 pv_sundown_end: int, pv_light_eff_lw: int,
                 pv_light_eff_std: int, pv_max_power: int):
        self._logfile = logfile
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._broker_queue = broker_queue
        self._broker_username = broker_username
        self._broker_password = broker_password
        self._pv_min = pv_min
        self._pv_max = pv_max
        self._output_file = output_file
        self._delimiter = delimiter
        self._max_execute_time = max_execute_time
        self._time_iter = time_iter
        self._execute_time_log = execute_time_log
        self._start_time = 0
        self._credentials = pika.PlainCredentials(self._broker_username,
                                                  self._broker_password)
        self._environment_pv = environment_pv
        self._pv_sunrise_start = self._get_fraction_time(pv_sunrise_start)
        self._pv_sunrise_end = self._get_fraction_time(pv_sunrise_end)
        self._pv_zenith = self._get_fraction_time(pv_zenith)
        self._pv_sundown_start = self._get_fraction_time(pv_sundown_start)
        self._pv_sundown_end = self._get_fraction_time(pv_sundown_end)
        self._pv_light_eff_lw = pv_light_eff_lw
        self._pv_light_eff_std = pv_light_eff_std
        self._pv_max_power = pv_max_power
        logging.basicConfig(filename=logfile, filemode="a", level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p')

    def _connect_broker(self):
        """
        Connects to broker. Returns channel.
        :return:
        """
        logging.info("PV: Connecting to broker")
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._broker_host,
                                          port=self._broker_port,
                                          credentials=self._credentials))
            channel = self._connection.channel()
            channel.basic_qos(prefetch_count=1)
            channel.queue_declare(queue=self._broker_queue, durable=True)
            return channel
        except pika.exceptions.ConnectionClosedByBroker as e:
            logging.error("PV: Connection to broker closed by broker: %s", e)
        except pika.exceptions.AMQPConnectionError as e:
            logging.error("PV: Connection to broker failed: %s", e)
        except Exception as e:
            logging.error("PV: Error: %s", e)
        else:
            logging.info("PV: Connected to broker")
        return None

    def start(self):
        """
        Connects to broker and receives meter's value.
        :return:
        """
        logging.info("PV: Starting PV")
        channel = self._connect_broker()
        if channel is not None:
            self._get_value_from_broker(channel)

    def _get_value_from_broker(self, channel: pika.channel.Channel):
        try:
            channel.basic_consume(queue=self._broker_queue,
                                  on_message_callback=self._callback)
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker as e:
            logging.error("PV: Connection to broker closed by broker: %s", e)
        except pika.exceptions.AMQPConnectionError as e:
            logging.error("PV: Connection to broker failed: %s", e)
        except KeyboardInterrupt as e:
            channel.stop_consuming()
            self._connection.close()
            logging.info("PV: Stopped PV")
        except Exception as e:
            logging.error("PV: Error: %s", e)

    def _callback(self, ch, method, properties, body):
        """
        Callback function for receiving meter's value.
        """
        logging.info(f"PV: Received message {body}")

        data_from_broker = body.decode("utf-8")
        command_meter, value = data_from_broker.split("::")
        if command_meter == "START":
            self._start_time = int(value)
        elif command_meter == "DATA":
            meter_day, meter_iteration, meter_reading = self._parse_data_string(
                value)
            if meter_reading < self._pv_min or meter_reading > self._pv_max:
                logging.info(
                    f"PV: Meter reading {meter_reading} is out of range")
            else:
                pv_value = self._generate_pv_value(meter_day, meter_iteration)
                data_record = {
                    "timestamp": meter_iteration,
                    "meter_value": meter_reading * -1,
                    "pv_value": pv_value,
                    "sum": pv_value - meter_reading,
                }
                logging.info(f"PV: Writing data record {data_record} to file")
                self._write_to_output(meter_day, data_record, command_meter)
        elif command_meter == "END":
            meter_day, meter_iteration, meter_reading = self._parse_data_string(
                value)
            filename = self._make_filename(meter_day)
            logging.info(f"PV: Renaming temporary file to {filename}")
            os.rename(filename + ".tmp", filename)
            self._make_plot(meter_day)
            data_file = open(self._execute_time_log, 'a')

            execution_time = int(datetime.now().timestamp()) - int(
                self._start_time)
            data_file.write(
                f"Execution time of {filename}: {execution_time} seconds\n")
            if execution_time > self._max_execute_time:
                logging.info(
                    f"PV: Execution time of {filename} is too long: {execution_time} seconds")
            data_file.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _make_plot(self, meter_day: int):
        """
        Drawing a plot of daily data.
        :param meter_day:
        :return:
        """
        filename = self._make_filename(meter_day)
        plot_filename = self._make_plot_filename(meter_day)
        logging.info(f"PV: Making plot to {plot_filename}")
        try:
            data_csv = pd.read_csv(filename, delimiter=";",
                                   index_col='timestamp')
            data_csv.plot()
            plt.savefig(plot_filename)
        except Exception as e:
            logging.error(f"PV: Can't plot data to {plot_filename}! Error: {e}")

    def _parse_data_string(self, data_string: str) -> List:
        """
        Parses data from broker and returns day, timestamp,
        generated value from meter.
        """
        meter_day, meter_iteration, meter_reading = data_string.split(
            self._delimiter)
        return [int(meter_day), int(meter_iteration), int(meter_reading)]

    def _make_filename(self, meter_day: int) -> str:
        """
        Makes filename for data file.
        :return:
        """
        if ".csv" in self._output_file:
            return self._output_file.split(".csv")[0] + "_day" + str(
                meter_day) + ".csv"
        return "day" + str(meter_day) + "_" + self._output_file

    def _make_plot_filename(self, meter_day: int) -> str:
        """
        Makes filename for plot file.
        :return:
        """
        if ".csv" in self._output_file:
            return self._output_file.split(".csv")[0] + "_day" + str(
                meter_day) + ".png"
        return "day" + str(meter_day) + "_" + self._output_file + ".png"

    def _write_to_output(self, meter_day: int, data_record: dict,
                         command_meter: str):
        """
        Writes data record to output file.
        :return:
        """
        filename = self._make_filename(meter_day) + ".tmp"
        new_day = False
        if not os.path.isfile(filename):
            new_day = True
        data_file = open(filename, 'a')
        if command_meter == "DATA":
            csv_writer = csv.writer(data_file, delimiter=self._delimiter)
            if new_day:
                csv_writer.writerow(["timestamp", "meter", "pv", "sum"])
            csv_writer.writerow(data_record.values())
        data_file.close()

    def _get_fraction_time(self, hour: int, minute: int = 0,
                           second: int = 0) -> float:
        """Convert time to fraction of the day"""
        return ((hour * 3600 + minute * 60) + second) / (24 * 3600)

    def _get_parabola_vertex(self, x1: float, y1: float, x2: float, y2: float,
                             x3: float,
                             y3: float) -> (float, float, float):
        """Calculate the vertex of a parabola given three points"""

        denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
        A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
        B = (x3 * x3 * (y1 - y2) +
             x2 * x2 * (y3 - y1) +
             x1 * x1 * (y2 - y3)) / denom
        C = (x2 * x3 * (x2 - x3) * y1 +
             x3 * x1 * (x3 - x1) * y2 +
             x1 * x2 * (x1 - x2) * y3) / denom

        return A, B, C

    def _morning_strgt(self, x: float) -> float:
        A = (self._pv_light_eff_lw * self._pv_max_power) / (
                self._pv_sunrise_end - self._pv_sunrise_start)
        B = A * self._pv_sunrise_start * -1
        return A * x + B

    def _evening_strgt(self, x: float) -> float:
        A = ((-self._pv_sunrise_end) * self._pv_max_power *
             self._pv_light_eff_lw) / (self._pv_sundown_end -
                                       self._pv_sundown_start)
        B = A * self._pv_sundown_end * -1
        return A * x + B

    def _parabola(self, x: float) -> float:
        """Calculate the parabola"""
        (A, B, C) = self._get_parabola_vertex(
            self._pv_sunrise_end, self._morning_strgt(self._pv_sunrise_end),
            self._pv_zenith, (self._pv_light_eff_std * self._pv_max_power),
            self._pv_sundown_start, self._evening_strgt(self._pv_sundown_start))
        return A * (x ** 2) + (B * x) + C

    def _generate_pv_value(self, meter_day: int, meter_iteration: int) -> int:
        """Generate PV curve using a straight for SUNRISE
        a parabola for ZENITH and another straight for SUNDOWN"""

        time = self._get_fraction_time(0, 0, meter_iteration * self._time_iter)

        if time >= self._pv_sunrise_start and time <= self._pv_sunrise_end:
            value = self._morning_strgt(time)
        elif time > self._pv_sunrise_end and time < self._pv_sundown_start:
            value = self._parabola(time)
        elif time >= self._pv_sundown_start and time <= self._pv_sundown_end:
            value = self._evening_strgt(time)
        else:
            value = 0.0

        return int(value)
