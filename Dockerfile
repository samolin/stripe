FROM python:3.10.5-slim


ENV PYTHONUNBUFFERED=1 \

  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \

  POETRY_VERSION=1.1.14 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock /usr/src/app/

# Install dependencies:
RUN pip3 install poetry
RUN poetry install
RUN python manage.py createsuperuser
RUN python manage.py migrate
# copy project
COPY . .
