FROM ubuntu:trusty-20160323

MAINTAINER zhoujunqian <zjqzero@gmail.com>


RUN apt-get -y install wget


RUN wget https://github.com/ekanite/ekanite/releases/download/v1.0.0/ekanited-v1.0.0-linux-amd64.tar.gz
RUN tar -xzf ekanited-v1.0.0-linux-amd64.tar.gz
RUN mv ekanited-v1.0.0-linux-amd64/ekanited /usr/sbin/ekanited
RUN rm -rf ekanited-v1.0.0-linux-amd64.tar.gz ekanited-v1.0.0-linux-amd64

RUN apt-get -y purge wget

CMD ["/usr/sbin/ekanited", "-datadir", "/var/ekanited", "-tcp", "0.0.0.0:5514", "-queryhttp", "0.0.0.0:8080", "-query", ""]
