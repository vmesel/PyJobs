FROM python:3.6
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY manage.py manage.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY /pyjobs/ /code/

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
