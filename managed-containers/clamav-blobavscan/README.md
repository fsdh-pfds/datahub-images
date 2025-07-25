# ClamAV Blob Antivirus Scanner

This containerized service scans Azure Blob Storage objects for viruses using **ClamAV**, automatically quarantining infected files and reporting scan results.

It’s designed to run as a background worker, consuming Azure Storage Queue messages that notify it of new or updated blobs.

---

## ✨ Features

- ✅ **Antivirus scanning with ClamAV**
- ✅ **Azure Blob Storage integration** (download & upload blobs)
- ✅ **Azure Queue integration** (consume messages about new blobs)
- ✅ **Automatic quarantining** of infected files
- ✅ **Configurable via environment variables**
- ✅ **Lightweight container image built on Ubuntu 24.04**

---

## 📂 Project Structure

```none
managed-containers/clamav-blobavscan/
├── Dockerfile             # Builds the container image
├── base_packages.list     # OS-level dependencies
├── README.md
└── app/
    ├── entrypoint.sh      # Container startup script
    ├── requirements.txt   # Python dependencies
    └── scan_blob.py       # Main scanning logic
```

---

## 🏗️ How It Works

1. **Receives blob event notifications** via Azure Queue messages.
2. **Downloads the blob** from Azure Blob Storage to a temporary location.
3. **Scans the blob** with ClamAV.
4. If clean ✅ → the blob remains in its original container.
5. If infected ❌ → it’s moved to a quarantine container.

Currently, **blob tagging is disabled** for hierarchical namespace-enabled storage accounts (like ADLS Gen2).

---

## 🔧 Configuration

The scanner is configured entirely with environment variables:

| Variable                    | Description                               | Default              |
| --------------------------- | ----------------------------------------- | -------------------- |
| `storage_connection_string` | Azure Storage connection string           | _required_           |
| `queue_name`                | Queue name containing blob events         | `blob-created`       |
| `container_name`            | Name of the container with incoming blobs | `datahub`            |
| `quarantine_container_name` | Name of the quarantine container          | `datahub-quarantine` |
| `AzureTenantId`             | Azure tenant (optional placeholder)       |                      |
| `AzureSubscriptionId`       | Azure subscription (optional placeholder) |                      |
| `DataHub_ENVNAME`           | Environment name (e.g. `dev`)             | `dev`                |

---

## 🚀 Quick Start

### 1️⃣ Build the image

```bash
docker build -t clamav-blobavscan .
```

### 2️⃣ Run locally

```bash
docker run --rm \
  -e storage_connection_string="YOUR_CONNECTION_STRING" \
  -e queue_name="blob-created" \
  -e container_name="datahub" \
  -e quarantine_container_name="datahub-quarantine" \
  clamav-blobavscan
```

The container will:

- Update ClamAV definitions (`freshclam`)
- Start scanning queued blob events

### 3️⃣ Push to GitHub Container Registry

```bash
docker tag clamav-blobavscan ghcr.io/YOUR_ORG/clamav-blobavscan
docker push ghcr.io/YOUR_ORG/clamav-blobavscan
```

---

---

## 🏗️ Deployment

This scanner is designed for:

- **Azure Functions** with custom containers
- **Kubernetes** as a worker pod
- **Standalone container execution**

You’ll need:

- An **Azure Storage Queue** receiving blob event notifications
- Proper IAM/Access keys for the container to access blob storage

---

## 📦 Dependencies

### OS Packages

Listed in `base_packages.list`, including:

- **ClamAV**
- **curl / wget / unzip**
- **Python3 + venv**

### Python Dependencies

From `requirements.txt`:

- `azure-storage-blob`
- `azure-storage-queue`
- `azure-identity`
- `azure-keyvault`

---

## 🛠️ Development

Run the container in interactive mode for debugging:

```bash
docker run -it --entrypoint bash clamav-blobavscan
```

Inside the container:

```bash
freshclam    # update virus DB
. /opt/venv/bin/activate
python3 scan_blob.py
```
