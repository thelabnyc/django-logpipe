FROM registry.gitlab.com/thelabnyc/python:py313@sha256:f66034dd9cb8e03d350cf81b6fba002f8241a1640d525ad1f77b6f3374e1c47b

RUN mkdir /code
WORKDIR /code

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

ADD . /code/
RUN poetry install

RUN mkdir /tox
ENV TOX_WORK_DIR='/tox'
