"""
Production runner script
Uses Gunicorn for production deployment
"""

import os
import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Process naming
proc_name = "ai_puzzle_game"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

print("=" * 60)
print("🚀 Starting AI Puzzle Game - Production Server")
print("=" * 60)
print(f"Workers: {workers}")
print(f"Bind: {bind}")
print(f"Timeout: {timeout}s")
print("=" * 60)

