**Project name:**
PV simulator challenge

**Description:**

This project is a challenge to simulate simple PV systems. It has 3 main parts:
- consumer's meter
- broker
- pv simulator

1. Meter.

Its simple application to simulate power meter of consumer. 
Meter application makes simulation of power consumption of consumer and send it to broker.

2. Broker.

I'm  using RabbitMQ to communicate with other applications. It received messages from meter(s) and send them to pv simulator(s).

3. PV simulator.

There is simple simulator of PV system. It receives meter's value from broker and simulate PV system. All information from PV system stored to output file.

**How to run:**

You should use Docker to run this project. 
1. Install and run Docker: https://docs.docker.com/engine/install/
2. Build and run project: docker-compose -f docker-compose.yml up --build
3. You can see output of "meter" and "pv simulator" in ./data/logs/ directory.
4. Result output is in ./data/log/ directory.

**Configurations**:

All required parameters set in docker-compose.yml file. For "DEV" mode you can use docker-compose-dev.yml file.
- BROKER_HOST  - hostname of broker (RabbitMQ)
- BROKER_PORT  - port of broker (RabbitMQ)
- BROKER_QUEUE - queue name of broker (RabbitMQ)
- BROKER_USERNAME - username of broker (RabbitMQ)
- BROKER_PASSWORD - password of broker (RabbitMQ)
- PV_MIN - minimal power of meter (W)
- PV_MAX - maximal power of meter (W)
- ITERATION - interval where sending values from meter (s)
- LOGFILE - name of log file
- DELIMITER - delimiter of log file
- OUTPUT_FILE - name of output file
- TIME_ITER - value is spacing between two data simulations (s)
- MAX_EXECUTE_TIME - if simulation time is more than this value, it will be noted in log file (s)
- EXECUTE_TIME_LOG - log file name for execute time of each daily simulation 
- PV_SUNRISE_START - sunrise start time (h) (got value from chart from main "homework" file)
- PV_SUNRISE_END - sunrise end time (h) (got value from chart from main "homework" file)
- PV_ZENITH - zenith time (h) (got value from chart from main "homework" file)
- PV_SUNDOWN_START - sundown start time (h) (got value from chart from main "homework" file)
- PV_SUNDOWN_END - sundown end time (h) (got value from chart from main "homework" file)
- PV_LIGHT_EFF_LW - light efficiency of light in sunrise and sunset time
- PV_LIGHT_EFF_STD - light efficiency of standard time
- PV_MAX_POWER - maximal power of PV system (W)

**Testing:**

Start project with "docker-compose -f docker-compose-dev.yml up --build" and run unit tests of each application.
Meter - "docker exec -ti meter python -m pytest"
PV Simulator - "docker exec -ti pv python -m pytest"


