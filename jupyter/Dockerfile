FROM ubuntu:16.04

MAINTAINER zjqzero@gmail.com

ADD notebook.sh /notebook.sh
RUN apt-get update
RUN apt-get install -y python-dev python-pip
RUN pip install jupyter

RUN rm -rf /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888



CMD ["/notebook.sh"]