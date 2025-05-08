# renovate: datasource=docker depName=ubuntu versioning=ubuntu
ARG UBUNTU_VERSION=24.04
FROM ubuntu:$UBUNTU_VERSION

# Enable headless mode
ENV DEBIAN_FRONTEND=noninteractive

COPY base_packages.list /tmp/base_packages.list
COPY addon_packages.list /tmp/addon_packages.list
COPY startup-scripts/ /startup-scripts/
COPY entrypoint.sh /entrypoint.sh

# Install base packages.list
# ./get-versions --list openssl ca-certificates jq curl gpg lsb-release git debsums liblttng-ust1t64 libicu74 wget
RUN apt-get update && \
    xargs -a /tmp/base_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install addon repositories 
# Terraform   
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg -o /tmp/hashicorp.gpg && \
    gpg --dearmor < /tmp/hashicorp.gpg > /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list

# Microsoft  
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.gpg && \
    gpg --dearmor < /tmp/microsoft.gpg > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list

# Docker    
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/docker.gpg && \
    gpg --dearmor < /tmp/docker.gpg > /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  
# Install addon packages.list
# ./get-versions azure-cli docker-ce docker-ce-cli containerd.io docker-ce-rootless-extras
RUN apt-get update && \
    xargs -a /tmp/addon_packages.list apt-get install -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash runner

# Rootless docker config
RUN echo "runner:100000:65536" >> /etc/subuid \
    && echo "runner:100000:65536" >> /etc/subgid
RUN groupadd -f docker \
 && usermod -aG docker runner

RUN chmod +x /entrypoint.sh \
    && chmod +x /startup-scripts/*.sh \
     && chown -R runner:runner /entrypoint.sh /startup-scripts

# Switch to unprivileged user and set entrypoint
USER runner
ENTRYPOINT ["/entrypoint.sh"]
