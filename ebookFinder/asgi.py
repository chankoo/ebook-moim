import os
import json

from django.core.asgi import get_asgi_application

config = {}
if os.path.isfile("./config.json"):
    with open("./config.json") as fp:
        config = json.load(fp)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"settings.{config.get('env', 'local')}")

application = get_asgi_application()
