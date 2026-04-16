FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:5e7e077145f451d6b8db8522b8b912ee318e2d074c6f64b8dce9248928517f00

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
