#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import json

config = {}
if os.path.isfile("./config.json"):
    with open("./config.json") as fp:
        config = json.load(fp)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"settings.{config.get('env', 'local')}")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
