FROM ubuntu:16.04

MAINTAINER zhoujunqian <zjqzero@gmail.com>

ADD start.sh /start.sh

RUN apt-get update
RUN apt-get install -y python python3 python-dev python3-dev python-pip python3-pip
RUN pip install jupyter ipython
RUN pip3 install jupyter ipython

RUN rm -rf /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888



CMD ["/start.sh"]
