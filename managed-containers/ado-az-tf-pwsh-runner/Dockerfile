FROM ubuntu:24.04@sha256:6015f66923d7afbc53558d7ccffd325d43b4e249f41a6e93eef074c9505d2233
LABEL org.opencontainers.image.description="ADO Linux (ubuntu) Self‑Hosted Runner image with Terraform, PowerShell and the Azure CLI"
LABEL org.opencontainers.image.source="https://github.com/fsdh-pfds/datahub-images"
LABEL org.opencontainers.image.url="https://github.com/fsdh-pfds/datahub-images/blob/main/managed-containers/ado-az-tf-pwsh-runner/README.md"

# Enable headless mode
ENV DEBIAN_FRONTEND=noninteractive

COPY base_packages.list /tmp/base_packages.list
COPY addon_packages.list /tmp/addon_packages.list

# Install baseline
RUN apt-get update && \
    xargs -a /tmp/base_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install addon repositories    
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg -o /tmp/hashicorp.gpg && \
    gpg --dearmor < /tmp/hashicorp.gpg > /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.gpg && \
    gpg --dearmor < /tmp/microsoft.gpg > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list
  
# Install addons
RUN apt-get update && \
    xargs -a /tmp/addon_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Powershell Modules
RUN pwsh -Command \
    "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop; \
    Install-Module -Name Az -RequiredVersion 14.0.0 -Scope AllUsers -Repository PSGallery -Force -AllowClobber; \
    Install-Module -Name SqlServer -RequiredVersion 22.3.0 -Scope AllUsers -Repository PSGallery -Force -AllowClobber"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd -m -s /bin/bash runner

# Switch to unprivileged user and set entrypoint
USER runner
ENTRYPOINT ["/entrypoint.sh"]
