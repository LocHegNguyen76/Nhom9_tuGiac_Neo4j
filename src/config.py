"""Đọc cấu hình kết nối Neo4j từ biến môi trường hoặc file .env."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
# File thông tin đăng nhập của Neo4j Aura dùng tên NEO4J_USERNAME -> nhận cả hai tên
NEO4J_USER = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "matkhau123")
# Để trống = dùng cơ sở dữ liệu mặc định của tài khoản (hợp cả Neo4j cài trên máy lẫn Aura)
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE") or None
# Máy chủ web (Render...) cấp cổng qua biến PORT
APP_PORT = int(os.environ.get("PORT") or os.environ.get("APP_PORT") or "5000")

# Tên hiển thị trên giao diện: không lộ địa chỉ máy chủ Aura khi chạy trên web
NEO4J_HIEN_THI = "Neo4j AuraDB (cloud)" if ".neo4j.io" in NEO4J_URI else NEO4J_URI
