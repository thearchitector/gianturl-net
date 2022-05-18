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


FROM python:3.8-slim as apibuilder

ENV PIP_NO_CACHE_DIR=1 \
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
RUN poetry install --remove-untracked --no-dev

# build the application
COPY api /gianturl
RUN poetry build -f wheel


FROM tiangolo/uvicorn-gunicorn:python3.8-slim as production

# user build args
ARG GROUPID=1000
ARG USERID=1000
ARG USERNAME=application

# configure env vars for runtime
ENV APP_NAME=gianturl \
    APP_MODULE="gianturl.app:app" \
    ACCESS_LOG="gianturl.log" \
    ERROR_LOG="gianturl.log" \
    PORT=8080 \
    ## configure python/poetry runtime settings
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONCOERCECLOCALE=0 \
    PYTHONUTF8=1 \
    HOME="/home/$USERNAME"

# setup production user
RUN groupadd -g "$GROUPID" "$USERNAME" && \
    useradd -lmu "$USERID" -g "$USERNAME" -s /bin/bash "$USERNAME"
USER "$USERNAME"

# copy the ui and api
WORKDIR "$HOME/app"
COPY entrypoint.sh entrypoint.sh
COPY --from=uibuilder /ui/public ui
COPY --from=apibuilder /gianturl/dist/gianturl-0.0.0-py3-none-any.whl ./

# install and launch the service
RUN python -m pip install --user *.whl
EXPOSE $PORT
CMD [ "./entrypoint.sh" ]