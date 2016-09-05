FROM ubuntu:trusty-20160323

MAINTAINER zhoujunqian <zjqzero@gmail.com>

ENV VERSION v1.1.0

RUN apt-get -y install wget


RUN wget https://github.com/ekanite/ekanite/releases/download/$VERSION/ekanited-$VERSION-linux-amd64.tar.gz
RUN tar -xzf ekanited-$VERSION-linux-amd64.tar.gz
RUN mv ekanited-$VERSION-linux-amd64/ekanited /usr/sbin/ekanited
RUN rm -rf ekanited-$VERSION-linux-amd64.tar.gz ekanited-$VERSION-linux-amd64

RUN apt-get -y purge wget

CMD ["/usr/sbin/ekanited", "-datadir", "/var/ekanited", "-tcp", "0.0.0.0:5514", "-queryhttp", "0.0.0.0:8080", "-query", ""]
