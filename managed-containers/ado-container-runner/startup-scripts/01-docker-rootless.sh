#!/usr/bin/env bash
set -euo pipefail

log() { echo "--> $*"; }

# ensure the runtime dir exists
export XDG_RUNTIME_DIR="$HOME/.docker"
mkdir -p "$XDG_RUNTIME_DIR"

# start the rootless Docker daemon in the background
log "Launching dockerd-rootless.sh…"
dockerd-rootless.sh --experimental &

# wait until it’s ready
until docker info &>/dev/null; do
  sleep 1
done

log "Docker rootless daemon is up"
export DOCKER_HOST="unix://$XDG_RUNTIME_DIR/docker.sock"
