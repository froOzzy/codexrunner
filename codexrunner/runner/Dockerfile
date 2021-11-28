FROM python:3.8-slim-buster

RUN mkdir cli && mkdir cli/files
COPY image/cli_runner.py cli/runner.py
COPY image/requirements.txt cli/requirements.txt
WORKDIR cli
RUN pip install -r requirements.txt