FROM --platform=linux/amd64 python:3.11

WORKDIR /app

ADD ruleengine /app/ruleengine/
ADD requirements.txt setup.py /app/
RUN python3 /app/setup.py install

ADD log_sim.py log_listener.py rules.py tailer.py /app/
ADD local.yaml /root/.config/cos/local.yaml
ADD config.yaml /root/.config/cos/config.yaml
ADD cos /usr/local/bin/cos
ADD sn.txt /root/.ros/sn.txt
ADD run_cos /usr/local/bin/run_cos
RUN mkdir /app/logs

ADD logSource /app/logSource/
