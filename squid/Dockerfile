FROM ubuntu:14.04

# So that we can run as unprivileged user inside the container.
RUN sed -i '/^nobody/d' /etc/passwd && echo 'nobody:x:99:99:nobody:/:/bin/sh' >> /etc/passwd

RUN apt-get update && apt-get install -y squid && rm -rf /var/lib/apt/lists/*

USER nobody

EXPOSE 3128

# The following flags have to be specified when starting this container:
# -network
# Refer to -help for documentation on them.
ENTRYPOINT ["/usr/sbin/squid3"]