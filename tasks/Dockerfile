FROM python:3.10-slim

RUN pip install poetry==2.4.1

WORKDIR /app

COPY pyproject.toml poetry.lock .

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

COPY src .