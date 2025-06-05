FROM registry.gitlab.com/thelabnyc/python:3.13.730@sha256:48ead35b07386d36b46420c486875cc8448690219158fd92f221546a6d4d4245

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
