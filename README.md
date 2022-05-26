**Project name:**
PV simulator challenge

**Description:**

This project is a challenge to simulate simple PV systems. It has 3 main parts:
- consumer's meter
- broker
- pv simulator

1. Meter
Its simple application to simulate power meter of consumer. 
Meter application makes simulation of power consumption of consumer and send it to broker.

2. Broker
I'm  using RabbitMQ to communicate with other applications. It received messages from meter(s) and send them to pv simulator(s).

3. PV simulator
There is simple simulator of PV system. It receives meter's value from broker and simulate PV system. All information about PV system is stored in output file.

**How to run:**

You should use Docker to run this project. 
1. Install and run Docker: https://docs.docker.com/engine/install/
2. Build and run project: docker-compose -f docker-compose.yml up --build
3. You can see output of "meter" and "pv simulator" in ./data/logs/ directory.
4. Result output is in ./data/log/ directory.

**Configurations**:

All required parameters set in docker-compose.yml file.
- BROKER_HOST  - hostname of broker (RabbitMQ)
- BROKER_PORT  - port of broker (RabbitMQ)
- BROKER_QUEUE - queue name of broker (RabbitMQ)
- BROKER_USERNAME - username of broker (RabbitMQ)
- BROKER_PASSWORD - password of broker (RabbitMQ)
- PV_MIN - minimal power of meter (W)
- PV_MAX - maximal power of meter (W)
- PV_DELAY - interval between sending values of meter (s) 
- BROKER_INITIAL_DELAY - initial delay of broker (s)
- LOGFILE - name of log file
- DELIMITER - delimiter of log file
- OUTPUT_FILE - name of output file

**Testing:**

Start project with "docker-compose -f docker-compose.yml up --build" and run unit tests of each application.
Meret - "docker exec -ti meter python -m unittest meter/tests/test_Meter.py"
PV Simulator - "docker exec -ti pv python -m unittest pv/tests/test_PV.py"


