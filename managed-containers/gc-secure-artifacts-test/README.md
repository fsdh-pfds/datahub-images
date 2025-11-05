# gc-secure-artifacts-test

A minimal and typical container image used to validate pulling from the **GC Secure Artifacts** JFrog instance. This image is managed and updated by Chainguard and is wired into GC Security Artifacts chainguard proxy.

> **Status**: Experimental. Intended for pipeline validation and end‑to‑end artifact flow testing.

---

## What this image is for

- Prove out **OIDC-based auth** from GitHub Actions to JFrog Artifactory (no long‑lived secrets).
- Provide a tiny runnable image for smoke tests (e.g., `docker pull` responds and exits cleanly).
