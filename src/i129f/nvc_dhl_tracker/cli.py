import os
import sys
from copy import copy

import django
from django.core.management import call_command


def run_from_cli():
    args = copy(sys.argv[1:])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "i129f.nvc_dhl_tracker.settings")
    django.setup()
    call_command("migrate")
    call_command("run_nvc_tracker", *args)


if __name__ == "__main__":
    """
    You can call this like

    ::

        python -m i129f.nvc_dhl_tracker.cli
    """
    run_from_cli()
