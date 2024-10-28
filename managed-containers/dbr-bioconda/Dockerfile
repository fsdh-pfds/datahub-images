# Stage 1: Builder for installing required packages
FROM ubuntu:20.04 AS builder

# Install wget, bzip2, and libdigest-sha-perl in the builder stage
RUN apt-get update && apt-get install -y wget bzip2 libdigest-sha-perl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Main container based on Databricks Runtime
FROM databricksruntime/python:12.2-LTS

# Create a non-root user and group
RUN groupadd -r myusergroup && useradd -r -g myusergroup myuser

# Copy necessary binaries from the builder stage
COPY --from=builder /usr/bin/wget /usr/bin/wget
COPY --from=builder /usr/bin/bzip2 /usr/bin/bzip2
COPY --from=builder /usr/lib/libdigest-sha-perl /usr/lib/libdigest-sha-perl

# Switch to non-root user for conda installation
USER myuser

# Install Miniconda at /home/myuser/miniconda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-py38_23.3.1-0-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && /bin/bash /tmp/miniconda.sh -b -p /home/myuser/miniconda \
    && rm /tmp/miniconda.sh

# Set Conda environment variables
ENV PATH="/home/myuser/miniconda/bin:$PATH"
ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda
ENV DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda

# Copy the environment file to the container
COPY --chown=myusergroup:myusergroup env.yml /home/myuser/.conda-env-def/env.yml

# Create the Conda environment from the YAML file
RUN conda env create --file /home/myuser/.conda-env-def/env.yml \
    && ln -s /home/myuser/miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Set Conda configurations
RUN conda config --system --set channel_priority strict \
    && conda config --system --set always_yes True

# Set the working directory
WORKDIR /home/myuser

# Add a HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
