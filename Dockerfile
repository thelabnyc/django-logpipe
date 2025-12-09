FROM registry.gitlab.com/thelabnyc/python:3.14@sha256:58ee440298b582ac3dab1cfeed3671b7c8a6b2f798a496c8ba423795328f26fb

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN uv sync

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
