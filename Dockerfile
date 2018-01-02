FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code

ADD requirements-dev.txt /code/

ADD requirements.txt /code/

RUN apt-get update -yq && apt-get upgrade -yq

RUN apt-get install python3-pip -yq

RUN pip install -r requirements-dev.txt

ADD . /code/
