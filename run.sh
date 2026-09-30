#!/usr/bin/env bash
# Chạy nhanh trên macOS/Linux:  bash run.sh
set -e
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
.venv/bin/python -m src.seed
.venv/bin/python app.py
