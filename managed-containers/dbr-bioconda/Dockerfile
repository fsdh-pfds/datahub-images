FROM databricksruntime/python:12.2-LTS

RUN apt update && apt install -y wget bzip2 libdigest-sha-perl

# Conda must be installed at /databricks/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-py38_23.3.1-0-Linux-x86_64.sh -O miniconda.sh \
    && /bin/bash miniconda.sh -b -p /databricks/conda \
    && rm miniconda.sh

COPY env.yml /databricks/.conda-env-def/env.yml

# Source conda.sh for all login shells.
RUN /databricks/conda/bin/conda env create --file /databricks/.conda-env-def/env.yml \
    && ln -s /databricks/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

RUN /databricks/conda/bin/conda config --system --set channel_priority strict \
     && /databricks/conda/bin/conda config --system --set always_yes True

ENV DEFAULT_DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda
ENV DATABRICKS_ROOT_CONDA_ENV=fsdh-bioconda