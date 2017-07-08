#from standard library
import os
import sys
import subprocess
import platform
import inspect
import argparse
import json
import smtplib
from email.mime.text import MIMEText

# from somebody else
import ipgetter

ADDRESS_FILE = './.ipfreely/current_ip_address.txt'
SETTINGS_FILE_PATH = './.ipfreely/'
SETTINGS_FILE = 'settings.txt'

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
args = parser.parse_args()


def get_script_dir(follow_symlinks=True):
    """get absolute path to currently running script

    follow_symlinks: bool
        if True, follow symlink to source path. Default is True.

    by J.F. Sebastian, https://stackoverflow.com/a/22881871/4906855
    """
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        script_path = os.path.abspath(sys.executable)
    else:
        script_path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        script_path = os.path.realpath(script_path)
    return os.path.dirname(script_path)


def persist_ip(ip):
    """writes ip to text file
    """
    f = open(ADDRESS_FILE, 'w')
    f.write(ip)
    f.close()


def read_saved_ip():
    """reads current ip
    """
    f = open(ADDRESS_FILE, 'r')
    savedIp = f.read()
    f.close()
    return savedIp


def check_ip(settings):
    """checks if ip has changes
    """
    currIP = ipgetter.myip()

    if not os.path.isfile(ADDRESS_FILE):
        # trigger the script to send email for the first time
        persist_ip('127.0.0.1')

    savedIP = read_saved_ip()

    if currIP != savedIP:
        for to_email in settings['to_email']:
            msg = MIMEText("Public IP address has changed from {0} to {1}"
                           .format(savedIP, currIP))
            msg['Subject'] = 'Alert - IP address has changed'
            msg['From'] = settings['from_email']
            msg['To'] = to_email

            # Send the message via our own SMTP server, but don't include the
            # envelope header.
            s = smtplib.SMTP('localhost')
            s.sendmail(settings['from_email'],
                       to_email,
                       msg.as_string())
            s.quit()

        persist_ip(currIP)


if __name__ == '__main__':
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
