FROM python:bullseye
MAINTAINER steveblackmon

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src app

WORKDIR /app

CMD flask --app app --debug run --host=0.0.0.0 