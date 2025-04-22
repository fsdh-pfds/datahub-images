FROM ghcr.io/actions/actions-runner@sha256:831a2607a2618e4b79d9323b4c72330f3861768a061c2b92a845e9d214d80e5b

USER root

COPY packages.list /tmp/packages.list

# Install additional dependencies from packages.list
RUN apt-get update && \
    xargs -a /tmp/packages.list apt-get install -y --no-install-recommends

# Clean up apt caches
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy custom entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to unprivileged user and set entrypoint
USER runner
ENTRYPOINT ["/entrypoint.sh"]
