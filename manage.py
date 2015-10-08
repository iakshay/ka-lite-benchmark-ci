#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    with open('.env') as env:
        content = env.readlines()
        for line in content:
            key, val = line.split('=')
            os.environ[key] = val.strip()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "benchmarkci.settings")

    print os.environ
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
