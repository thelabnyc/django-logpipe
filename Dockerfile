FROM registry.gitlab.com/thelabnyc/python:3.13.783@sha256:4f4509973f8d880e58df5b2828dafea0c690140580b4b519aec93b527e609ca4

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
