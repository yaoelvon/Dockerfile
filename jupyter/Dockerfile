FROM ubuntu:16.04

MAINTAINER zjqzero@gmail.com

RUN apt-get update
RUN apt-get install python-dev python-pip
RUN pip install jupyter

RUN rm /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888

ADD notebook.sh /

CMD ["/notebook.sh"]