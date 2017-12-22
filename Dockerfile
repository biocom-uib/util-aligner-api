FROM python:3.6-alpine
WORKDIR /opt

ENV PYTHONPATH=/opt/
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2

ADD requirements*.txt /opt/

RUN apk add --no-cache ca-certificates

ARG INCLUDE_TEST=0
ARG INCLUDE_DEV=0

RUN REQUIREMENTS_FILE="requirements.txt"; \
    if [ $INCLUDE_TEST == 1 ]; then \
        REQUIREMENTS_FILE="${REQUIREMENTS_FILE} requirements-test.txt"; \
    fi; \
    if [ $INCLUDE_DEV == 1 ]; then \
        REQUIREMENTS_FILE="${REQUIREMENTS_FILE} requirements-dev.txt"; \
    fi; \ 
    grep -hv ".txt" ${REQUIREMENTS_FILE} > /tmp/requirements.txt  && \
    pip install -r /tmp/requirements.txt