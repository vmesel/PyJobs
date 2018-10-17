FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code

COPY /pyjobs/ /code/
COPY requirements.txt /code/

RUN pip install -r requirements.txt
