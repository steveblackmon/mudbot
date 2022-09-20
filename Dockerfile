FROM python:bullseye
MAINTAINER steveblackmon

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src app

VOLUME ["/conf"]

WORKDIR /app

ENTRYPOINT ["python", "app.py"]