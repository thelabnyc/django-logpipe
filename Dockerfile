FROM registry.gitlab.com/thelabnyc/python:3.13.665@sha256:3825e9b2679b1c361ffabf582bdab3d9e3d752c6ea684da23839716aa3bb5263

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
