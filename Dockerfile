FROM python:3.8.5-slim
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY here-comes-a-secret-key  # merely a mock to allow collectstatic

WORKDIR /code
COPY Makefile Makefile
COPY manage.py manage.py
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN apt-get update && \
    apt-get install -y make git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -U pip && \
    pip install -U poetry && \
    poetry install

COPY pyjobs/ /code/pyjobs/
RUN  make migrate
RUN  make collectstaticdocker
