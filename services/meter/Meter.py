import logging
import time
from datetime import datetime
from random import randint

import pika

class Meter:
    """
    Meter class simulates consumer meter. Class generates random value between
    pv_min and pv_max (Watt) and publish value to broker.
    Should provide broker's host, port, queue, username, password.
    Class publishes meter's value every pv_delay seconds.
    """

    def __init__(self, broker_host: str, broker_port: int, broker_queue: str,
                 broker_username: str,
                 broker_password: str, pv_min: int, pv_max: int,
                 iteration: int, logfile: str, environment_pv: str,
                 delimiter: str):

        self._logfile = logfile
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._broker_queue = broker_queue
        self._broker_username = broker_username
        self._broker_password = broker_password
        self._pv_min = pv_min
        self._pv_max = pv_max
        self._iteration = iteration
        self._total_iterations = 24 * 60 * 60 / self._iteration
        self._credentials = pika.PlainCredentials(self._broker_username,
                                                  self._broker_password)
        self._environment_pv = environment_pv
        self._delimiter = delimiter
        logging.basicConfig(filename=logfile, filemode="a", level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S %p')

    def _connect_broker(self):
        """
        Connects to broker and returns channel.
        """
        logging.info("Meter: Connecting to broker: %s", self._broker_host)
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self._broker_host,
                                          port=self._broker_port,
                                          credentials=self._credentials))
            channel = self._connection.channel()
            channel.queue_declare(queue=self._broker_queue, durable=True)
            channel.confirm_delivery()
            return channel
        except pika.exceptions.ConnectionClosedByBroker as e:
            logging.error("Meter: Connection to broker closed by broker: %s", e)
        except pika.exceptions.AMQPConnectionError as e:
            logging.error("Meter: Connection to broker failed: %s", e)
        except Exception as e:
            logging.error("Meter: Error: %s", e)
        return None

    def start(self):
        """
        Coneects to broker and starts meter simulator.
        """
        logging.info("Meter: Connecting to broker: %s", self._broker_host)
        channel = self._connect_broker()
        if channel is not None:
            self._current_day = 0

            while True:
                data_to_send = f"START::{int(datetime.now().timestamp())}"
                try:
                    self._publish_meter_to_broker(channel, data_to_send)
                except KeyboardInterrupt:
                    logging.info("Meter: Exiting meter simulator")
                    break
                self._current_iteration = 1
                while self._current_iteration <= self._total_iterations:
                    try:
                        meter = self._generate_meter(self._current_iteration)
                        data_to_send = f"DATA::{self._make_string_to_broker(meter)}"
                        self._publish_meter_to_broker(channel, data_to_send)
                        self._current_iteration += 1
                        # time.sleep(self._pv_delay)
                    except KeyboardInterrupt:
                        logging.info("Meter: Exiting meter simulator")
                        break
                data_to_send = f"END::{self._make_string_to_broker(0)}"
                try:
                    self._publish_meter_to_broker(channel, data_to_send)
                except KeyboardInterrupt:
                    logging.info("Meter: Exiting meter simulator")
                    break
                self._current_day += 1
                time.sleep(3)
        self._connection.close()

    def _generate_meter(self, current_iteration: int) -> int:
        """
        Generates random value between pv_min and pv_max (Watt)
        """
        return randint(self._pv_min, self._pv_max)

    def _make_string_to_broker(self, meter: int) -> str:
        """
        Makes string to broker.
        """
        return f"{self._current_day}{self._delimiter}" \
               f"{self._current_iteration}{self._delimiter}" \
               f"{meter}"

    def _publish_meter_to_broker(self, channel, data_to_send: str):
        """
        Publishes value to broker.
        """
        logging.info("Meter: Publishing meter to broker: %s", data_to_send)
        try:
            channel.basic_publish(exchange='', routing_key=self._broker_queue,
                                  body=data_to_send,
                                  properties=pika.BasicProperties(
                                      delivery_mode=2))
        except pika.exceptions.ConnectionClosedByBroker as e:
            logging.error("Meter: Connection to broker closed by broker: %s", e)
        except pika.exceptions.AMQPConnectionError as e:
            logging.error("Meter: Connection to broker failed: %s", e)
        except Exception as e:
            logging.error("Meter: Error while publishing PV: %s", e)
