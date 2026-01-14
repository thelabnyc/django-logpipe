FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:c2cfe032f91c6077f8046c2e0dc91f313888f5dcdc583399f966e85083935eb9

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
