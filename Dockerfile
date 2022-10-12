FROM python:bullseye
MAINTAINER steveblackmon

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src app

VOLUME ["/conf"]

WORKDIR /app

ENV TERM xterm-256color

ENTRYPOINT ["python", "app.py"]