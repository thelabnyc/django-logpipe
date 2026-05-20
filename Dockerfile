FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:09299bb7ce1a015c916a26c924a6a86151eb123464cddab469fb1ec3c1d4992d

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
