FROM ghcr.io/metpx/sarracenia:development

RUN pip3 --no-cache install paho-mqtt redis python-redis-lock

WORKDIR /root

CMD sr3 foreground --config $SR3_CONFIG --logStdout --no $SR3_INSTANCE