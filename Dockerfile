FROM alpine:latest

RUN apk --update add \
    supervisor \
    python3 && \
    rm -rf /var/cache/apk/*

COPY server.py /
COPY NetThermPrintServer.py /


ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD supervisord -c /etc/supervisor/conf.d/supervisord.conf
