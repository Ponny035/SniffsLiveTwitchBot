FROM python:3.10-rc-buster

ENV env prod

ENV msg msgon

WORKDIR /app

COPY /rootfs/requirements.txt /app

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY /rootfs /app

CMD ["python3", "-u", "launcher.py"]
