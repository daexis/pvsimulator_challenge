import csv
import logging
from datetime import datetime
from random import randint

import pika


class Pv:
    """
    Class receiving consumer's meter value from a broker, generating PV value and writing to a file.
    Should provide broker's host, port, queue, username, password.
    """

    def __init__(self, broker_host: str, broker_port: int, broker_queue: str, broker_username: str,
                 broker_password: str,
                 pv_min: int, pv_max: int,
                 output_file: str, delimiter: str, logfile: str, environment_pv: str):
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
        self._credentials = pika.PlainCredentials(self._broker_username, self._broker_password)
        self._environment_pv = environment_pv
        logging.basicConfig(filename=logfile, filemode="a", level=logging.INFO,
                            format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %p')

    def _connect_broker(self):
        """
        Connects to broker. Returns channel.
        :return:
        """
        logging.info("PV: Connecting to broker")
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(self._broker_host, port=self._broker_port, credentials=self._credentials))
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
            channel.basic_consume(queue=self._broker_queue, on_message_callback=self._callback)
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

        meter_reading = int(body)
        if meter_reading < self._pv_min or meter_reading > self._pv_max:
            logging.info(f"PV: Meter reading {meter_reading} is out of range")
        else:
            pv_value = self._generate_pv_value()
            data_record = {
                "timestampt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "meter_value": meter_reading,
                "pv_value": pv_value,
                "sum": meter_reading + pv_value
            }
            logging.info(f"PV: Writing data record {data_record} to file")
            self._write_to_output(data_record)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _generate_pv_value(self) -> int:
        """
        Generates PV value. It generates random value between pv_min and pv_max.
        :return:
        """
        return randint(self._pv_min, self._pv_max)

    def _write_to_output(self, data_record: dict):
        """
        Writes data record to output file.
        :param data_record:
        :return:
        """
        data_file = open(self._output_file, 'a')
        csv_writer = csv.writer(data_file, delimiter=self._delimiter)
        csv_writer.writerow(data_record.values())
        data_file.close()
