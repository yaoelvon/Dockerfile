FROM ubuntu:16.04

MAINTAINER zhoujunqian <zjqzero@gmail.com>

ADD start.sh /start.sh

RUN apt-get update
RUN apt-get install -y python python3 python-dev python-pip
RUN pip install jupyter

RUN rm -rf /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888



CMD ["/start.sh"]
