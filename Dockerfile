FROM registry.gitlab.com/thelabnyc/python:py313@sha256:06acdbcbdbcab477a36d268b35fecaa79d1632422bb4547058610531248ce76a

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
