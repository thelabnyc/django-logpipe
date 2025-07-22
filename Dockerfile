FROM registry.gitlab.com/thelabnyc/python:3.13.834@sha256:9038b22c083371bd9d3dcd0c88cd0f091a1e0bd946b7030a5b7a505c1e57dd1d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
