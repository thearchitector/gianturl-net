# syntax=docker/dockerfile:1.2


FROM node:16-alpine as uibuilder

# install node dependencies
WORKDIR /ui
COPY ui/package.json ui/pnpm-lock.yaml /ui/
RUN corepack enable && \
    pnpm install

# build source files
COPY ui /ui
RUN pnpm run build


FROM python:3.7-slim as production

# copy boot scripts from remote
COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /start-reload.sh /start-reload.sh
COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /start.sh /start.sh
COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /gunicorn_conf.py /gunicorn_conf.py

# configure env vars for runtime
ENV APP_NAME=gianturl \
    APP_MODULE="gianturl.app:app" \
    ACCESS_LOG="/var/log/gianturl.log" \
    ERROR_LOG="/var/log/gianturl.log" \
    PORT=8080 \
    ## configure python/poetry runtime settings
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONCOERCECLOCALE=0 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME=/etc/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1 \
    PATH="/etc/poetry/bin:$PATH"

# install system dependencies and poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get autoremove --purge && \
    rm -rf /var/lib/apt/lists/* && \
    poetry config virtualenvs.create false

# copy install python dependencies
WORKDIR /gianturl
COPY api/pyproject.toml api/poetry.lock /gianturl/
RUN poetry install --remove-untracked --no-dev -E deployment

# copy the rest of everything
COPY api /gianturl
COPY --from=uibuilder /ui/public ui

# launch the service
EXPOSE $PORT
CMD [ "/gianturl/bin/entrypoint.sh" ]