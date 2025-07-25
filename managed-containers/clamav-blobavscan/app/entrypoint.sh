#!/bin/bash

touch "$0".start
freshclam

python3 scan_blob.py
