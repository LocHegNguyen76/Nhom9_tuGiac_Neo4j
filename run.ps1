# Chạy nhanh trên Windows PowerShell:  .\run.ps1
# (Nếu bị chặn script: Set-ExecutionPolicy -Scope Process Bypass)
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m src.seed
.\.venv\Scripts\python.exe app.py
