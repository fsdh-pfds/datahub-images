# renovate: datasource=docker depName=ubuntu versioning=ubuntu
ARG UBUNTU_VERSION=24.04@sha256:6015f66923d7afbc53558d7ccffd325d43b4e249f41a6e93eef074c9505d2233
FROM ubuntu:$UBUNTU_VERSION

# Enable headless mode
ENV DEBIAN_FRONTEND=noninteractive
ENV PROJ_CD= PROJ_RG= PROJ_STORAGE_ACCT= PROJ_KV= PROJ_SUB= CLIENT_ID=


COPY base_packages.list /tmp/base_packages.list
COPY addon_packages.list /tmp/addon_packages.list

# Install base packages.list
RUN apt-get update && \
    xargs -a /tmp/base_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install addon repositories    
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.gpg && \
    gpg --dearmor < /tmp/microsoft.gpg > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list
  
# Install addon packages.list
RUN apt-get update && \
    xargs -a /tmp/addon_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Powershell Modules
RUN pwsh -Command \
    "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop; \
    Install-Module -Name Az -RequiredVersion 14.0.0 -Scope AllUsers -Repository PSGallery -Force -AllowClobber; \
    Install-Module -Name SqlServer -RequiredVersion 22.3.0 -Scope AllUsers -Repository PSGallery -Force -AllowClobber; \
    Install-Module -Name Az.Accounts -RequiredVersion 5.3.0 -Scope AllUsers -Repository PSGallery -Force -AllowClobber; \
    Install-Module -Name Az.ServiceBus -RequiredVersion 4.1.1 -Scope AllUsers -Repository PSGallery -Force -AllowClobber"

# Create unprivileged user
RUN useradd -m -s /bin/bash runner

# Switch to unprivileged user and set entrypoint
USER runner
COPY app/ /app/

CMD ["pwsh", "-f", "/app/sas.ps1"]