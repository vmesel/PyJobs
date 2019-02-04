FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY manage.py manage.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install pipenv & \
    pipenv install --system --deploy --dev

COPY /pyjobs/ /code/
