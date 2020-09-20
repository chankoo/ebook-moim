#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ebookFinder.settings.local')
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
