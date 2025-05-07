from waitress import serve
from core.wsgi import application


serve(application, listen='*:9090', threads=120, log_socket_errors=False)