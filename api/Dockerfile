FROM hayd/deno:latest

EXPOSE 8000

WORKDIR /app

COPY /rootfs/app /app

RUN deno cache server.ts

CMD ["run", "--allow-net", "--allow-read", "server.ts"]