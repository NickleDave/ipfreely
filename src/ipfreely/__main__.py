import sys
import subprocess
import platform

import json

from . import argparser
from .constants import CONFIG_ROOT, SETTINGS_PATH
from .util import check_ip, get_script_dir


def cli(args):
    if len(sys.argv) < 2:
        if not SETTINGS_PATH.exists():
            raise FileNotFoundError('ipfreely did not find settings file.\n'
                                    'To create the settings file, run the '
                                    'script using the command line arguments.\n'
                                    'Run \"ipfreely -h\" or \"ipfreely --help\"'
                                    'to see all arguments.')

        else:
            with SETTINGS_PATH.open('r') as fp:
                settings = json.load(fp)
            if 'from_email' not in settings:
                raise KeyError('from_email is not set in settings file')
            elif 'password' not in settings:
                raise KeyError('password is not set in settings file')
            elif 'to_email' not in settings:
                raise KeyError('to_email is not set in settings file')
            else:
                check_ip(settings)

    else:  # if there were command line arguments
        if SETTINGS_PATH.exists():
            with SETTINGS_PATH.open('r') as fp:
                settings = json.load(fp)
        else:
            settings = {}
            CONFIG_ROOT.mkdir(exist_ok=True)

        if any([hasattr(args, arg) for arg in ['from_email',
                                               'password',
                                               'to_email',
                                               'name']]):
            if args.from_email:
                settings['from_email'] = args.from_email
            if args.password:
                settings['password'] = args.password
            if args.to_email:
                if 'to_email' in settings:
                    to_list = settings['to_email']
                else:
                    to_list = []
                to_list.append(args.to_email)
                settings['to_email'] = to_list
            if args.name:
                settings['name'] = args.name

            with SETTINGS_PATH.open('w') as fp:
                json.dump(settings, fp)

        if args.activate or args.deactivate:
            if platform.system() == 'Windows':
                schtasks = "c:\windows\System32\schtasks.exe"
                python_path = sys.executable()
                ipfreely_path = get_script_dir()
                if args.activate:
                    schargs = " /Create /SC HOURLY /TN 'ipfreely' /TR "
                elif args.deactivate:
                    schargs = " /Delete /TN 'ipfreely' /TR "
                popen_str = schtasks + schargs + python_path + " " + ipfreely_path

                subprocess.Popen(popen_str)

            elif platform.system() == 'Linux':
                if args.activate():
                    # https://stackoverflow.com/questions/610839/how-can-i-programmatically-create-a-new-cron-job
                    """echo "0 1 * * * /root/test.sh" | tee - a / var / spool / cron / root"""

            elif platform.system() == 'Darwin':
                pass


def main():
    parser = argparser.get_parser()
    args = parser.parse_args()
    cli(args)


if __name__ == '__main__':
    main()
