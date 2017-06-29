#from standard library
import os
import sys
import argparse
import json
import smtplib
from email.mime.text import MIMEText

# from somebody else
import ipgetter

ADDRESS_FILE = './.ipfreely/current_ip_address.txt'
SETTINGS_FILE = './.ipfreely/settings.txt'

parser = argparse.ArgumentParser(description='Checks ip address and sends an email'
                                             ' when it changes. To check ip, run '
                                             'scripts with no command line arguments.')
parser.add_argument('-f', '--from_email',
                    help='email address from which to send alerts when ip address changes')
parser.add_argument('-t', '--to_email',
                    help='email address to which alert emails should be sent')
parser.add_argument('-n', '--name',
                    help='name for this computer (in case you have ipfreely running on'
                    ' multiple computers')
args = parser.parse_args()


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


def check_ip(settings_file):
    """checks if ip has changes
    """
    currIP = ipgetter.myip()

    if not os.path.isfile(ADDRESS_FILE):
        # trigger the script to send email for the first time
        persist_ip('127.0.0.1')

    savedIP = read_saved_ip()

    if currIP != savedIp:
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
                                    'Run \"ipconfig -h\" or \"ipconfig --help\"'
                                    'to see all arguments.')

        else:
            with open(SETTINGS_FILE, 'r') as settings_file:
                settings = json.load(settings_file)
            if 'from_email' not in settings:
                raise KeyError('from_email is not set in settings file')
            elif 'to_email' not in settings:
                raise KeyError('to_email is not set in settings file')
            else:
                check_ip(settings)

    else:  # if there were command line arguments
        with open(SETTINGS_FILE, 'r') as settings_file:
            settings = json.load(settings_file)

        if args.from_email:
            settings['from_email'] = args.from_email
        if args.to_email:
            to_list = settings['to_email']
            to_list.append(args.to_email)
            settings['to_email'] = to_list
        if args.name:
            settings['name'] = args.name

        with open(SETTINGS_FILE, 'w') as settings_file:
            json.dump(settings, settings_file)
