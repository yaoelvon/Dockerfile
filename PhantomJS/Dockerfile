FROM ubuntu:trusty-20160323

MAINTAINER ZhouJunQian <zjqzero@gmail.com>

ENV PHANTOMJS_VERSION 2.1.1

RUN apt-get update

RUN apt-get -y install libfreetype6 libfontconfig wget

RUN wget --no-check-certificate --no-proxy -O /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
    tar -xjf /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 -C /tmp && \
    rm -f /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64.tar.bz2 && \
    mv /tmp/phantomjs-$PHANTOMJS_VERSION-linux-x86_64/bin/phantomjs /usr/local/bin && \
    apt-get autoremove -y && \
    apt-get clean all && \
    rm -rf /tmp/*

CMD ["/usr/bin/phantomjs"]
