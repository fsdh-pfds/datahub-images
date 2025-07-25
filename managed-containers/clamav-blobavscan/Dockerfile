FROM python:3.12-bookworm

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

RUN apt update && apt install -y clamav clamav-daemon curl wget unzip python3-venv && rm -rf /var/lib/apt/lists/*
#RUN freshclam
COPY app/ /app/
WORKDIR /app

RUN python3 -m venv $VIRTUAL_ENV \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

CMD ["bash", "/app/entrypoint.sh"]