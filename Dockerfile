FROM registry.gitlab.com/thelabnyc/python:py313@sha256:efecf1d54180e040a131baaed3a12437ec8f3510372e87d7d9d4919d145db10e

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
