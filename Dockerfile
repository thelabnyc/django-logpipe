FROM registry.gitlab.com/thelabnyc/python:3.13.686@sha256:a63b93e18b1148955f237c55ec8aa45a9ab503ee3d3652900d9fdef57c64b67d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
