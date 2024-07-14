import os

from django.core.asgi import get_asgi_application


def check_local_uname():
    import platform

    return "linuxkit" in platform.uname().release


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "settings.local" if check_local_uname() else "settings.cloud",
)

application = get_asgi_application()
