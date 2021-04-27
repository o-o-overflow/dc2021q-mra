FROM python:3.8-alpine

ENV TERM linux

run apk update && apk add --no-cache netcat-openbsd bash curl

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY check1.sh /
COPY exploit.py /

