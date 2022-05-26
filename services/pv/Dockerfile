FROM python:3.9

ADD __main__.py /usr/src/pv/__main__.py
ADD PV.py /usr/src/pv/PV.py
ADD tests/test_PV.py /usr/src/pv/tests/test_PV.py
ADD requirements.txt /usr/src


WORKDIR /usr/src

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "pv"]