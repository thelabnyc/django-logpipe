FROM registry.gitlab.com/thelabnyc/python:3.13.723@sha256:b9aeb7d415f98544842bd03b3a5365219c9caf23ad8bdc1cb6b4e59ae16436b5

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
