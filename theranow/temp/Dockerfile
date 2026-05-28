FROM alpine:3.14

ENV PYTHONUNBUFFERED=1
ENV LOCAL_BIN=/home/kivy/.local/bin

RUN adduser kivy -D

RUN apk add --update --no-cache openjdk17 zip unzip python3 git --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community

RUN ln -sf python3 /usr/bin/python && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools buildozer cython

USER kivy

ENTRYPOINT ["buildozer"]
