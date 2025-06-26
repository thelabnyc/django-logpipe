FROM registry.gitlab.com/thelabnyc/python:3.13.777@sha256:e87fb3ad08282b6c09205c998c72b4ca0a25eb362b7ce84555b616d1063d0707

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
