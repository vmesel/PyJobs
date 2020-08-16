FROM python:3.7.4-slim
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY here-comes-a-secret-key  # merely a mock to allow collectstatic

WORKDIR /code
COPY Makefile Makefile
COPY manage.py manage.py
COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y make && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -U pip && \
    pip install -r requirements.txt

COPY pyjobs/ /code/pyjobs/
RUN  python manage.py collectstatic --no-input
