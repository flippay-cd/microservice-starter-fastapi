# syntax=docker/dockerfile:1

ARG CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
FROM ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}{{ docker_build_image }} AS build-base

ARG CI_SERVER_HOST
ARG CI_JOB_TOKEN
ARG CI_USER=gitlab-ci-token

ENV \
    # python
    # prevents python from buffering stdout and stderr
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # uv
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # https://taskfile.dev/
    TASK_VERSION=3.41.0

RUN \
    set -ex \
    # install system dependencies
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    # install task
    && wget --progress=dot:giga https://github.com/go-task/task/releases/download/v${TASK_VERSION}/task_linux_amd64.tar.gz \
    && tar -C /usr/local/bin -xzvf task_linux_amd64.tar.gz \
    && rm task_linux_amd64.tar.gz \
    && chown root:root /usr/local/bin/task

RUN pip install uv
RUN printf "machine ${CI_SERVER_HOST}\nlogin ${CI_USER}\npassword ${CI_JOB_TOKEN}" >> /root/.netrc && chmod og-rw /root/.netrc


FROM build-base AS build-app
WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --locked --no-install-project --no-default-groups


FROM build-app AS build-dev
RUN uv sync --locked --no-install-project


ARG CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
FROM ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}{{ docker_image }} AS base
ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:$PYTHONPATH \
    PATH=/app/.venv/bin:$PATH \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    TZ=Europe/Moscow

RUN \
    set -ex \
    # create a non-root user
    && addgroup --gid 10001 app && adduser --uid 10000 --gid 10001 app \
    # install system dependencies
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    locales \
    libpq-dev \
    gettext \
    netcat-traditional \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/* \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["task"]
CMD ["http:run:prod"]

COPY --from=build-base /usr/local/bin/task /usr/local/bin/task

FROM base AS app
USER 10000
COPY --from=build-app /app/.venv /app/.venv
COPY . /app


FROM base AS dev
USER 10000
COPY --from=build-dev /app/.venv /app/.venv
COPY . /app
