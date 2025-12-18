FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:0e41570605a9add60854b464b5d6af7f367406efc2ee75e6a222da7d3f03d390

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
