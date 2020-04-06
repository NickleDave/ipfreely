import sys
import subprocess
import platform

import json

from . import argparser
from . import cron
from .constants import CONFIG_ROOT, SETTINGS_PATH
from .util import check_ip, send

CONFIG_OPTIONS = ['from', 'to', 'password', 'name', 'mode']


def _get_settings():
    """helper function to get settings"""
    if not SETTINGS_PATH.exists():
        raise FileNotFoundError('ipfreely did not find settings file.\n'
                                'To create the settings file, run the '
                                'script using the command line arguments.\n'
                                'Run \"ipfreely -h\" or \"ipfreely --help\"'
                                'to see all arguments.')

    with SETTINGS_PATH.open('r') as fp:
        settings = json.load(fp)

    for config_option in CONFIG_OPTIONS:
        if config_option not in settings:
            raise ValueError(
                f'could not execute command because config option {config_option} is not set in settings file.'
                f'Set it by executing: $ ipfreely config --{config_option} <value>'
            )

    return settings


def cli(args):
    """command-line interface logic"""
    if args.command == 'send':
        settings = _get_settings()
        send(settings)

    elif args.command == 'check':
        settings = _get_settings()
        check_ip(settings)

    elif args.command == 'config':
        # check for config dir, either get settings from it or if it doesn't exist create it
        if SETTINGS_PATH.exists():
            # don't use "_get_settings" here because we don't want to
            # throw an error about a setting that's not in the file when the user is trying to set it
            with SETTINGS_PATH.open('r') as fp:
                settings = json.load(fp)
        else:
            settings = {}
            CONFIG_ROOT.mkdir(exist_ok=True)

        # update any settings specified by user
        for config_option in CONFIG_OPTIONS:
            if hasattr(args, config_option):
                settings[config_option] = getattr(args, config_option)

        # save config again
        with SETTINGS_PATH.open('w') as fp:
            json.dump(settings, fp)

    elif args.command =='activate' or args.command == 'deactivate':
        settings = _get_settings()

        os = platform.system()
        if os == 'Windows':
            schtasks = "c:\windows\System32\schtasks.exe"
            python_path = sys.executable()
            if args.command == 'activate':
                schargs = " /Create /SC HOURLY /TN 'ipfreely' /TR "
            elif args.command == 'deactivate':
                schargs = " /Delete /TN 'ipfreely' /TR "
            popen_str = schtasks + schargs + python_path + f" -m ipfreely {settings['mode']}"
            subprocess.Popen(popen_str)

        elif os == 'Linux' or os == 'Darwin':
            cron.add_cron_lines(
                cron_lines=f"0 * * * * python -m ipfreely {settings['mode']}"
            )


def main():
    parser = argparser.get_parser()
    args = parser.parse_args()
    cli(args)


if __name__ == '__main__':
    main()
