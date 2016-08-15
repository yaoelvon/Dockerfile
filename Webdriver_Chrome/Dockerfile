FROM ubuntu:trusty-20160323

MAINTAINER ZhouJunQian <zjqzero@gmail.com>

COPY ./google-chrome.list /etc/apt/sources.list.d

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A040830F7FAC5991
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1397BC53640DB551


RUN apt-get update

RUN apt-get -y install xdg-utils \
                       google-chrome-stable \
                       xvfb \
                       x11-xkb-utils \
                       xfonts-100dpi \
                       xfonts-75dpi \
                       xfonts-scalable \
                       xfonts-cyrillic \
                       wget \
                       unzip

RUN wget http://chromedriver.storage.googleapis.com/2.9/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin

RUN apt-get autoremove -y && \
    apt-get clean all && \
    rm -rf /tmp/* && \
    rm -rf /var/lig/apt/lists/*

CMD ["/usr/local/bin/chromedriver"]
