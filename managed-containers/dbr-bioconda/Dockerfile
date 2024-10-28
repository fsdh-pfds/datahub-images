# Stage 1: Builder for installing required packages
FROM ubuntu:20.04 AS builder

# Install wget, bzip2, and libdigest-sha-perl in the builder stage
RUN apt update && apt install -y wget bzip2 libdigest-sha-perl

# Stage 2: Main container based on Databricks Runtime
FROM databricksruntime/python:12.2-LTS

# Create a non-root user and group
RUN groupadd -r myusergroup && useradd -r -g myusergroup myuser

# Copy necessary binaries from the builder stage
COPY --from=builder /usr/bin/wget /usr/bin/wget
COPY --from=builder /usr/bin/bzip2 /usr/bin/bzip2
COPY --from=builder /usr/lib/libdigest-sha-perl /usr/lib/libdigest-sha-perl

# Install Miniconda at /databricks/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-py38_23.3.1-0-Linux-x86_64.sh -O miniconda.sh \
    && /bin/bash miniconda.sh -b -p /databricks/conda \
    && rm miniconda.sh

# Copy the environment file to the container
COPY env.yml /databricks/.conda-env-def/env.yml

# Create the Conda environment from the YAML file
RUN /databricks/conda/bin/conda env create --file /databricks/.conda-env-def/env.yml \
    && ln -s /databricks/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Set Conda configurations
RUN /databricks/conda/bin/conda config --system --set channel_priority strict \
    && /databricks/conda/bin/conda config --system --set always_yes True

# Set environment variables
ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda
ENV DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda

# Set the working directory and switch to the non-root user
WORKDIR /home/myuser
USER myuser

# Add a HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
