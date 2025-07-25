#!/bin/bash
set -e

touch "$0".start
freshclam

. /opt/venv/bin/activate
python3 scan_blob.py
