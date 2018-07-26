FROM python:3.6-alpine

ARG APP_ENV=production

ENV APP_ENV=$APP_ENV
ENV PYTHONUNBUFFERED=1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk add --update --no-cache freetype libpng openblas libstdc++ \
    && apk add --no-cache --virtual .build-deps gcc g++ make git libffi libffi-dev openssl openssl-dev freetype-dev libpng-dev openblas-dev \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install numpy==1.13.3 \
    && pip install -r /requirements/${APP_ENV}.txt \
    && rm -rf /requirements \
    && apk del .build-deps

COPY ./docker/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod 777 /gunicorn.sh

WORKDIR /opt
