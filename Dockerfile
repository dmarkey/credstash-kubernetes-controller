FROM alpine:3.5
RUN apk update
RUN apk add gcc musl-dev python3 python3-dev libffi-dev openssl-dev && pip3 install kubernetes==8.0.0 && pip3 install credstash==1.15.0
ADD controller.py /root
ENTRYPOINT  ["python3", "-u", "/root/controller.py"]
