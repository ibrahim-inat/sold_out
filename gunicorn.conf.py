# Gunicorn configuration file

import multiprocessing

bind = "0.0.0.0:8000"
workers = 3
timeout = 60
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True
