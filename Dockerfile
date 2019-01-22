FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY /pyjobs/ /code/

