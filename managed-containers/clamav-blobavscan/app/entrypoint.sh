#!/bin/bash
set -e

touch "$0".start
freshclam

# shellcheck disable=SC1091
. /opt/venv/bin/activate
python3 scan_blob.py
