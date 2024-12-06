FROM docker.io/library/python:3.12-bookworm AS python
FROM mcr.microsoft.com/azure-functions/python:4-python3.12 AS azure-function

FROM python AS requirements

WORKDIR /function-app

ENV VENV_PATH="/function-app/venv"
ENV PYTHONDONTWRITEBYTECODE=1
ENV     PYTHONUNBUFFERED=1 
ENV LANG=C.UTF-8
ENV PATH="$VENV_PATH/bin:$PATH"

COPY requirements.txt .

RUN python -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install \
        --no-cache-dir \
        --use-pep517 \
        --requirement requirements.txt && \
    rm -rf requirements.txt

FROM azure-function AS deployment

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/home/site/wwwroot \
    PYTHONUNBUFFERED=1 \
    PATH="/function-app/venv/bin:$PATH"

COPY --from=requirements /function-app/venv /function-app/venv

# Copy the application code
WORKDIR /home/site/wwwroot
COPY function_app.py /home/site/wwwroot/

HEALTHCHECK CMD curl --fail http://localhost:80/health || exit 1

EXPOSE 80