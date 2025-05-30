# renovate: datasource=docker depName=ubuntu versioning=ubuntu
ARG UBUNTU_VERSION=24.04@sha256:6015f66923d7afbc53558d7ccffd325d43b4e249f41a6e93eef074c9505d2233
FROM ubuntu:$UBUNTU_VERSION

# Enable headless mode
ENV DEBIAN_FRONTEND=noninteractive

# Install baseline
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssl ca-certificates jq curl gpg lsb-release git debsums liblttng-ust1t64 libicu74 wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install addon repositories    
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.gpg && \
    gpg --dearmor < /tmp/microsoft.gpg > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list
  
# Install enhancements
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssl azure-cli powershell && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd -m -s /bin/bash runner

# Switch to unprivileged user and set entrypoint
USER runner
ENTRYPOINT ["/entrypoint.sh"]
