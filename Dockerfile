FROM registry.gitlab.com/thelabnyc/python:3.13.676@sha256:f6f734c00fce8b38ad0e5d43333104f15faec05a79638de1ec7f63aaafedd3e2

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
