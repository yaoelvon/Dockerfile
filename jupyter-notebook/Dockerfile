FROM ubuntu:16.04

MAINTAINER zhoujunqian <zjqzero@gmail.com>

ADD start.sh /start.sh
ADD requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install -y python python3 python-dev python3-dev python-pip python3-pip
RUN pip3 install jupyter ipython
RUN python2 -m pip install ipykernel
RUN python2 -m ipykernel install --user

RUN pip install -r requirements2.txt
RUN pip3 install -r requirements3.txt

RUN rm -rf /var/lib/apt/lists/*

VOLUME /notebooks
WORKDIR /notebooks

EXPOSE 8888



CMD ["/start.sh"]
