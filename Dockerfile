FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:c85a264b8085b45ee2eb31c2cdffa84fa3f013cfe36a0950391268715e0357af

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
