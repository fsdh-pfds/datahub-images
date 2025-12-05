FROM alpine@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c

# Install dependencies in one layer, without caching the index.     
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
