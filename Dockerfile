FROM registry.gitlab.com/thelabnyc/python:3.13.1016@sha256:5e034cec3b2222da7d6c994e875681f5fbdd15b8163903a1f0d84ab4313bb05c

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
