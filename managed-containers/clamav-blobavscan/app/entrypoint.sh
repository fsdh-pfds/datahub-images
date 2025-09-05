#!/bin/bash
set -e

touch "$0".start
freshclam
mkdir -p /var/run/clamav && chown clamav:clamav /var/run/clamav && (echo "TCPSocket 3310"; echo "StreamMaxLength 1G"; echo "MaxScanSize 8G"; echo "MaxFileSize 2G") >>/etc/clamav/clamd.conf
clamd

# shellcheck disable=SC1091
. /opt/venv/bin/activate
python3 scan_blob.py
