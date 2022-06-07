import csv
import logging
import os
from datetime import datetime
from random import randint
from typing import List

import pika


class Pv:
    """
    Class receiving consumer's meter value from a broker, generating PV value
    and writing to a file.
    Should provide broker's host, port, queue, username, password.
    """

    def __init__(self, broker_host: str, broker_port: int, broker_queue: str,
                 broker_username: str,
                 broker_password: str,
                 pv_min: int, pv_max: int,
                 output_file: str, delimiter: str, logfile: str,
                 environment_pv: str, max_execute_time: int, execute_time_log: str):
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
        self._execute_time_log = execute_time_log
        self._start_time = 0
        self._credentials = pika.PlainCredentials(self._broker_username,
                                                  self._broker_password)
        self._environment_pv = environment_pv
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
                    "timestampt": meter_iteration,
                    "meter_value": meter_reading,
                    "pv_value": pv_value,
                    "sum": meter_reading + pv_value
                }
                logging.info(f"PV: Writing data record {data_record} to file")
                self._write_to_output(meter_day, data_record, command_meter)
        elif command_meter == "END":
            meter_day, meter_iteration, meter_reading = self._parse_data_string(
                value)
            data_file = open(self._execute_time_log, 'a')
            filename = self._make_filename(meter_day)
            data_file.write(
                f"Execution time of {filename}: "\
                f"{int(datetime.now().timestamp()) - int(self._start_time)}"\
                f" seconds\n")
            data_file.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _parse_data_string(self, data_string: str) -> List:
        meter_day, meter_iteration, meter_reading = data_string.split(
            self._delimiter)
        return [int(meter_day), int(meter_iteration), int(meter_reading)]

    def _generate_pv_value(self, meter_day: int, meter_iteration: int) -> int:
        """
        Generates PV value. It generates random value between pv_min and pv_max.
        :return:
        """
        return randint(self._pv_min, self._pv_max)

    def _make_filename(self, meter_day: int) -> str:
        """
        Makes filename for data file.
        :return:
        """
        if ".csv" in self._output_file:
            return self._output_file.split(".csv")[0] + "_day" + str(
                meter_day) + ".csv"
        return "day" + str(meter_day) + "_" + self._output_file

    def _write_to_output(self, meter_day: int, data_record: dict,
                         command_meter: str):
        """
        Writes data record to output file.
        :return:
        """
        filename = self._make_filename(meter_day)
        new_day = False
        if not os.path.isfile(filename):
            new_day = True
        data_file = open(filename, 'a')
        if command_meter == "DATA":
            csv_writer = csv.writer(data_file, delimiter=self._delimiter)
            if new_day:
                csv_writer.writerow(["timestampt", "meter", "pv", "sum"])
            csv_writer.writerow(data_record.values())
        data_file.close()
