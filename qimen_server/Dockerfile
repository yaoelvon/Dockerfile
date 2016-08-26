FROM alpine:latest

MAINTAINER zhoujunqian <zjqzero@gmail.com>

RUN apk update
RUN apk add python py-pip
RUN pip install SQLAlchemy xmltodict jsoncompare
COPY ./*.* /var/app/qimen_server
RUN touch /var/app/__init__.py
RUN rm -rf /var/cache/apk/*

ENV PYTHONPATH /var/app

WORKDIR /var/app/qimen_server

EXPOSE 8080

CMD ["python", "test_server.py"]
