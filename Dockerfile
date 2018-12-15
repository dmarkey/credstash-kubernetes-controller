FROM alpine:3.5
RUN apk update &&  apk add libffi openssl python3 && apk add gcc musl-dev python3-dev libffi-dev openssl-dev && pip3 install kubernetes==8.0.0 && pip3 install credstash==1.15.0 && apk del openssl-dev libffi-dev python3-dev musl-dev gcc && rm -f /var/cache/apk/*
ADD controller.py /root
ENTRYPOINT  ["python3", "-u", "/root/controller.py"]
