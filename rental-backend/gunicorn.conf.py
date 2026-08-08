"""Gunicorn configuration for production deployment."""
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
workers = min(workers, 4)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
errorlog = "-"
accesslog = "-"
loglevel = "info"

# Process naming
proc_name = "rental-backend"

# Server mechanics
preload_app = True
daemon = False
tmp_upload_dir = None

# SSL (uncomment when certs are available)
# certfile = "/etc/ssl/certs/rental.pem"
# keyfile = "/etc/ssl/private/rental.key"
