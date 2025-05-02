FROM registry.gitlab.com/thelabnyc/python:3.13.660@sha256:d1a36f578df6b7eea0cb17bc35770a8aec3f86484bfd7bc5afc31255fc0d9ceb

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
