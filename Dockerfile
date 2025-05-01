FROM registry.gitlab.com/thelabnyc/python:py313@sha256:e1ed3aaeb702ac20c0340dcb09ae51d125738cabaa48516df73e98eb733fa91d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
