# proj-cost-worker

A minimal, pinned Ubuntu-based container that **monitors Azure project spend** and can enforce budget limits by **disabling a Customer-Managed Key (CMK)** in **Azure Key Vault**. Intended to run non-interactively (cron/ACI/Kubernetes Job) using a **Managed Identity**.

---

> **Architecture**: This image **must be built and published as `linux/amd64`**. All build/push commands below include `--platform linux/amd64`. Keep it single-arch unless you’ve validated multi-arch at runtime.

---

## What it does

- Reads configured **project budget** from environment variables.
- Retrieves **current spend** from Azure Consumption APIs for:

  - The main project Resource Group.
  - An optional Databricks Resource Group.

- Compares total spend against the budget.
- If budget is exceeded:
  - Optionally disables the **CMK** in Key Vault (if `PROJ_ENFORCE=true`).

Logic lives in `app/cost.ps1` and is the container’s default command.

---

## Requirements

- Azure Subscription with enabled **Consumption APIs**.
- Resource Groups mapped to the project.
- Key Vault containing CMK (`project-cmk`).
- Runtime identity (system or user-assigned) with rights to:
  - **Read costs** via `Get-AzConsumptionUsageDetail`.
  - **Update keys** in Key Vault (to disable CMK if enforced).

> If identity lacks Key Vault permissions, CMK enforcement will fail even if cost data retrieval succeeds.

---

## Image design highlights

- Ubuntu 24.04 pinned by digest + **apt snapshot** via `SNAPSHOT_ID`.
- Package versions pinned in `base_packages.list` / `addon_packages.list`.
- PowerShell + Az modules at fixed versions.
- Supports injection of custom Root CA (`ROOT_CA`).
- Runs as **non-root** user `runner`.

---

## Build (amd64)

### Docker Hub

```bash
# login first
echo "$DOCKERHUB_PAT" | docker login -u <your-user> --password-stdin

# build amd64
docker build \
  --platform=linux/amd64 \
  -t <your-user>/proj-cost-worker:latest \
  managed-containers/proj-cost-worker

# push
docker push <your-user>/proj-cost-worker:latest
```

### GitHub Container Registry (buildx, amd64)

```bash
docker buildx create --use --name xbuilder || true

docker buildx build \
  --platform linux/amd64 \
  -t ghcr.io/<org-or-user>/proj-cost-worker:latest \
  managed-containers/proj-cost-worker \
  --push
```

### Local load as amd64 (for testing on ARM Macs)

```bash
docker buildx build \
  --platform linux/amd64 \
  -t <your-user>/proj-cost-worker:dev \
  managed-containers/proj-cost-worker \
  --load
```

### Verify the pushed image is amd64

```bash
docker buildx imagetools inspect <image-ref>
```

> Keep the base image digest current (Renovate hint is present) and update `SNAPSHOT_ID` when advancing apt snapshots.

---

## Run examples

### Local test (budget enforcement on)

```bash
docker run --rm \
  -e PROJ_CD=abc \
  -e PROJ_RG=rg-abc \
  -e PROJ_DBR_RG=rg-abc-dbr \
  -e PROJ_BUDGET=5000.00 \
  -e PROJ_ENFORCE=true \
  -e PROJ_KV=kv-abc \
  -e PROJ_SUB=<subscription-guid> \
  <image-ref>
```

---

## Custom trust (optional Root CA)

If you inject at runtime via `ROOT_CA`, the script writes a temporary bundle to `/tmp/custom-root-ca.crt`. Point clients explicitly if needed:

```bash
export CURL_CA_BUNDLE=/tmp/custom-root-ca.crt
export REQUESTS_CA_BUNDLE=/tmp/custom-root-ca.crt
export NODE_EXTRA_CA_CERTS=/tmp/custom-root-ca.crt
```

---

## Logging & exit behavior

- Logs current project spend and budget comparison.

- On budget exceeded:

  - If enforcement enabled → disables CMK and logs action.
  - If enforcement disabled → logs warning only.

- Exit codes:
  - `0` success (budget within limits or enforcement applied).
  - Non-zero on authentication, subscription, or Key Vault errors.

---

## Troubleshooting

- **Managed identity login fails** → confirm `CLIENT_ID` or fallback identity is available.
- **KV update denied** → verify Key Vault RBAC or Access Policy.
- **429 TooManyRequests** → script includes retry logic; increase delays if needed.
- **Permission denied** → running as non-root; fix mounts/ownership or rebuild with `--chown`.

---

## File layout

```none
proj-cost-worker/
├─ Dockerfile                # pinned base + apt snapshot + Az modules
├─ base_packages.list        # minimal pinned packages
├─ addon_packages.list       # addons (PowerShell)
├─ app/
│  └─ cost.ps1               # budget monitoring + enforcement logic
└─ README.d
```
