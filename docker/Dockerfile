FROM python:3.9-alpine

ARG APP_ENV=base

ENV APP_ENV=$APP_ENV
ENV PYTHONUNBUFFERED=1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk add --update --no-cache freetype libpng jpeg openblas libstdc++ \
    && apk add --no-cache --virtual .build-deps gcc g++ make git libffi libffi-dev openssl openssl-dev freetype-dev libpng-dev jpeg-dev openblas-dev \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install -r /requirements/${APP_ENV}.txt \
    && rm -rf /requirements \
    && apk del .build-deps

COPY ./gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod 777 /gunicorn.sh

WORKDIR /opt
