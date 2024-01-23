#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def check_local_uname():
    import platform
    return 'linuxkit' in platform.uname().release

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local' if check_local_uname() else 'settings.cloud')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
