FROM registry.gitlab.com/thelabnyc/python:3.13.728@sha256:1ff284a07264c47ef7da6b83c9d2f4efee2d72d8c5734d307dd95e6a28758d44

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
