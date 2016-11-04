docker-celery-flower
====================

A simple Dockerfile to get an installation of Flower up and running as fast as possible.

Flower: https://github.com/mher/flower

Celery: http://www.celeryproject.org/

How to use
----------

The following example shows how to connect to a RabbitMQ broker used with Celery and you have
the RabbitMQ management plugin installed.

Download the docker image

    docker pull zjqzero/flower

Run the image in the foreground

    docker run -ti -p 5555:5555 ] -e CELERY_BROKER_URL=amqp://guest:guest@<broker_ipaddr>:5672// zjqzero/flower --broker_api=http://<username>:<password>@<hostname>:15672/api/

    docker run -d -p 5555:5555 -e CELERY_BROKER_URL=redis://<ipaddr>:6379/0 zjqzero/flower --broker_api=redis://<ipaddr>:6379/0 -basic_auth=<username>:<password>

Flower should be running on http://127.0.0.1:5555 (if you're running boot2docker you'll need to use
boot2docker's IP address instead)
