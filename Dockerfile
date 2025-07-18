FROM registry.gitlab.com/thelabnyc/python:3.13.828@sha256:7b95840c3577ee0e370971ff25aff2fceb82661a1b652ae7b4d3368deb3ecb05

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
