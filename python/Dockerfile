FROM python:3.9-slim-buster

ENV env prod

ENV msg msgon

WORKDIR /app

COPY /rootfs /app

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "launcher.py"]