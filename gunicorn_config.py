import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'hospital_app'

# SSL (if not using nginx)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 