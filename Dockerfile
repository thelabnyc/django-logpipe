FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:ffec4a4346c29efb891073411492115f111f13fe49acbec20a7f15e7947713d3

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
