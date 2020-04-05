"""utility functions"""
from email.mime.text import MIMEText
import inspect
import os
import smtplib
import sys

from ipgetter2 import ipgetter1 as ipgetter

from .constants import ADDRESS_FILE

__all__ = [
    'check_ip',
    'get_script_dir',
    'persist_ip',
    'read_saved_ip',
]


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
