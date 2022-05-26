FROM python:3.9

ADD __main__.py /usr/src/meter/__main__.py
ADD Meter.py /usr/src/meter/Meter.py
ADD tests/test_Meter.py /usr/src/meter/tests/test_Meter.py
ADD requirements.txt /usr/src

WORKDIR /usr/src

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "meter"]

