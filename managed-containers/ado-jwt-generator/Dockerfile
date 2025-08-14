FROM alpine@sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1

# Install dependencies in one layer, without caching the index
RUN apk add --no-cache \
    ca-certificates=20241121-r1 \
    curl=8.12.1-r1 \
    jq=1.7.1-r0 \
    openssl=3.3.3-r0


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup -S jwt \
 && adduser  -S -G jwt jwt

USER jwt
ENTRYPOINT ["/entrypoint.sh"]
