# Cấu hình gunicorn khi chạy trên máy chủ web (Render...). Lệnh chạy: gunicorn app:app
# (gunicorn không chạy trên Windows; trên máy mình vẫn dùng: python app.py)
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1          # gói miễn phí chỉ có 512 MB RAM
threads = 4          # vẫn phục vụ được nhiều người cùng lúc
timeout = 120        # lần đầu kết nối Neo4j Aura có thể chậm
accesslog = "-"
