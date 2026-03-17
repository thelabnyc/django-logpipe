FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:ab831a06a29a37bb133444e7f151563f4e0f5e2caf23359cd8076a09be5a510c

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
