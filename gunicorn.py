from multiprocessing import cpu_count
from os import environ

def max_workers():
    return cpu_count() * 2 + 1

bind = "unix:/var/run/gunicorn/ebook-moim.socket"
pidfile = "/var/run/gunicorn/ebook-moim.pid"
backlog = 2048
worker_connection = 1000
worker_class = 'gevent'
workers = max_workers()
loglevel = 'debug'
accesslog = '/var/log/gunicorn/gunicorn.product.acess.log'
errorlog = '/var/log/gunicorn/gunicorn.product.error.log'
timeout = 300
