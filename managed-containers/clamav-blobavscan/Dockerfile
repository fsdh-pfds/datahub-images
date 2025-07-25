FROM python:3.13-bookworm@sha256:645df645815f1403566b103b2a2bb07f6a01516bbb15078ed004e41d198ba194 as build

ENV VIRTUAL_ENV=/opt/venv \
    DEBIAN_FRONTEND=noninteractive

# Install ca-certificates
# hadolint ignore=DL3008
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* 

ARG SNAPSHOT_ID=20250725T145500Z
RUN echo "APT::Snapshot \"${SNAPSHOT_ID}\";" \
     > /etc/apt/apt.conf.d/50snapshot

RUN apt-get update && apt-get install -y --no-install-recommends clamav clamav-daemon curl wget unzip python3-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY app/ /app/
WORKDIR /app

RUN python3 -m venv $VIRTUAL_ENV \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest@sha256:2fa2e1d5396c78a166f4efa26d1661d89629d897d6c71a00c53d951427d2e8c0 AS runtime

ENV DataHub_ENVNAME=dev \   
    AzureTenantId= \
    AzureSubscriptionId= \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    AzureWebJobsDashboard= \
    storage_connection_string= \
    queue_name=blob-created \
    container_name=datahub \
    quarantine_container_name=datahub-quarantine \
    VIRTUAL_ENV=/opt/venv

COPY --from=build /opt/venv /opt/venv
COPY --from=build /app /app

WORKDIR /app

CMD ["bash", "/app/entrypoint.sh"]