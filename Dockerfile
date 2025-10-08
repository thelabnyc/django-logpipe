FROM registry.gitlab.com/thelabnyc/python:3.13.996@sha256:165008c6afc5769c149ce66e2a212ef4c8a22672e0be2e0802697df2f487f1b9

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
