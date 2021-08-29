FROM python:3.6-alpine

LABEL maintainer="Sergey Kornev <paladin705@yandex.ru>"

ENV TZ="Europe/Moscow"

ENV DB_NAME=
ENV DB_USER=
ENV DB_PASSWORD=
ENV DB_HOST=

ENV FLASK_ROUTE_PATH='/control_panel/'

WORKDIR /control_panel

RUN apk update \
    && apk upgrade \
    && apk add tzdata \
    && apk add git build-base postgresql-dev libffi-dev \
    && mkdir uploads

COPY control_panel.py deploy requirements.txt ./

RUN pip3 install gunicorn \
    && pip3 install -r requirements.txt \
    && chmod +x deploy

COPY app ./app

ENV FLASK_APP control_panel.py

CMD ./deploy ${DB_NAME} ${DB_USER} ${DB_PASSWORD} ${DB_HOST} ${FLASK_ROUTE_PATH} ${TZ}
