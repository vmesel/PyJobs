FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY here-comes-a-secret-key  # merely a mock to allow collectstatic

WORKDIR /code
COPY manage.py manage.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install -U pip && \
    pip install -U pipenv && \
    pipenv install --system --dev

COPY pyjobs/ /code/pyjobs/
RUN  python manage.py collectstatic --no-input
