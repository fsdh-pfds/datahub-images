FROM ghcr.io/actions/actions-runner@sha256:831a2607a2618e4b79d9323b4c72330f3861768a061c2b92a845e9d214d80e5b

USER root

COPY package.list /tmp/package.list

RUN apt-get update && \
    xargs -a /tmp/package.list apt-get install -y --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER runner
ENTRYPOINT ["./entrypoint.sh"]
