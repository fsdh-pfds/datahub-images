#!/bin/bash

touch $0.start
freshclam

. fsdh/bin/activate && python3 scan_blob.py
