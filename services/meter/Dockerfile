FROM python:3.9

ADD __main__.py /usr/src/meter/__main__.py
ADD Meter.py /usr/src/meter/Meter.py
ADD tests/test_Meter.py /usr/src/meter/tests/test_Meter.py
ADD requirements.txt /usr/src
ADD entrypoint.sh /usr/src/meter/entrypoint.sh
WORKDIR /usr/src

RUN pip install -r requirements.txt
RUN apt-get update -yqq \
  && apt-get install -yqq --no-install-recommends \
    netcat \
  && apt-get -q clean

#ENTRYPOINT ["python", "-m", "meter"]
ENTRYPOINT ["sh", "/usr/src/meter/entrypoint.sh"]
