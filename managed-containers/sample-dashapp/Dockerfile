# Base image for setting up dependencies
FROM cgr.dev/chainguard/python:latest-dev AS python-base

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv venv

# Add virtual environment to the PATH
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Final production image
FROM cgr.dev/chainguard/python@sha256:52820d1718fe1263cb8459cf7db1b136bcdf4758ac7f6dff7599d309ebd3eaf8 AS final

# Set working directory
WORKDIR /app

# Copy virtual environment from the base image
COPY --from=python-base /app/venv /app/venv

# Add virtual environment to the PATH
ENV PATH="/app/venv/bin:$PATH"

# Copy the application code
COPY app.py app.py

# Expose the port the application will use
EXPOSE 80

# Run as a non-root user for security purposes
USER nonroot

# Add a health check to ensure the container is functioning correctly
HEALTHCHECK CMD curl --fail http://localhost:80/health || exit 1

# Set entry point to run the application
ENTRYPOINT ["python", "app.py"]
