import os
import sys
import subprocess
import platform

import argparse
import json

from .constants import SETTINGS_FILE, SETTINGS_FILE_PATH
from .util import check_ip, get_script_dir


def cli(args):
    if len(sys.argv) < 2:
        if not os.path.isfile(SETTINGS_FILE):
            raise FileNotFoundError('ipfreely did not find settings file.\n'
                                    'To create the settings file, run the '
                                    'script using the command line arguments.\n'
                                    'Run \"ipfreely -h\" or \"ipfreely --help\"'
                                    'to see all arguments.')

        else:
            with open(SETTINGS_FILE_PATH + SETTINGS_FILE,
                      'r') as settings_file:
                settings = json.load(settings_file)
            if 'from_email' not in settings:
                raise KeyError('from_email is not set in settings file')
            elif 'password' not in settings:
                raise KeyError('password is not set in settings file')
            elif 'to_email' not in settings:
                raise KeyError('to_email is not set in settings file')
            else:
                check_ip(settings)

    else:  # if there were command line arguments
        if os.path.isfile(SETTINGS_FILE_PATH + SETTINGS_FILE):
            with open(SETTINGS_FILE_PATH + SETTINGS_FILE,
                      'r') as settings_file:
                settings = json.load(settings_file)
        else:
            settings = {}
            os.makedirs(SETTINGS_FILE_PATH, exist_ok=True)
        if any([hasattr(args.arg) for arg in ['from_email',
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

            with open(SETTINGS_FILE_PATH + SETTINGS_FILE, 'w+') as settings_file:
                json.dump(settings, settings_file)
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


def get_parser():
    parser = argparse.ArgumentParser(description='Checks ip address and sends an email'
                                                 ' when it changes. To check ip, run '
                                                 'scripts with no command line arguments.')
    parser.add_argument('-f', '--from_email',
                        help='email address from which to send alerts when ip address changes')
    parser.add_argument('-p', '--password',
                        help='password for \'from\' email address. Don\'t use one you care about.')
    parser.add_argument('-t', '--to_email',
                        help='email address to which alert emails should be sent')
    parser.add_argument('-n', '--name',
                        help='name for this computer (in case you have ipfreely running on'
                        ' multiple computers')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--activate',
                        help='sets script to run as a cron job')
    group.add_argument('-d', '--deactivate',
                        help='takes script off cron job list')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    cli(args)


if __name__ == '__main__':
    main()
