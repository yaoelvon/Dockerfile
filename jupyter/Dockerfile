FROM ubuntu:16.04

MAINTAINER zjqzero@gmail.com

RUN apt-get update
RUN apt-get install -y python-dev python-pip
RUN pip install jupyter

RUN rm -rf /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888

COPY ./notebook.sh /notebook.sh

CMD ["/notebook.sh"]