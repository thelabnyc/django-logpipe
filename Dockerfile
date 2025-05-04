FROM registry.gitlab.com/thelabnyc/python:3.13.662@sha256:e8cfdded2803e80be114029a669c10247a0825e97d0a3f77f482c5ce69d473c8

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
