FROM ubuntu:latest

LABEL org.opencontainers.image.authors="Peter.Silva@ssc-spc.gc.ca"

ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    BUILD_PACKAGES="build-essential" 

RUN apt-get update &&\ 
    apt-get install -y python3-amqp python3-appdirs python3-dateparser python3-humanfriendly \
        python3-humanize python3-jsonpickle python3-netifaces python3-paramiko python3-pip \
        python3-psutil python3-watchdog python3-magic

RUN pip3 --no-cache install paho-mqtt redis python-redis-lock
RUN pip3 --no-cache install metpx-sr3

WORKDIR /root

CMD sr3 foreground --config $SR3_CONFIG --logStdout --no $SR3_INSTANCE