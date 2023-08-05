FROM python:3.11

WORKDIR /app

ADD ruleengine /app/ruleengine/
ADD requirements.txt setup.py /app/
RUN python3 /app/setup.py install
