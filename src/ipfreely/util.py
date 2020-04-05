"""utility functions"""
from email.mime.text import MIMEText
import inspect
import os
import smtplib
import ssl
import sys

from ipgetter2 import ipgetter1 as ipgetter

from .constants import CURRENT_IP_ADDRESS_PATH

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
    """writes ip to text file"""
    with CURRENT_IP_ADDRESS_PATH.open('w') as fp:
        fp.write(ip)


def read_saved_ip():
    """reads current ip"""
    with CURRENT_IP_ADDRESS_PATH.open('r') as fp:
        saved_ip = fp.read()
    return saved_ip


PORT = 465


def check_ip(settings):
    """checks if ip has changed"""
    curr_ip = ipgetter.myip()

    if not CURRENT_IP_ADDRESS_PATH.exists():
        # make a fake ip to trigger the script to send email for the first time
        persist_ip('127.0.0.1')

    saved_ip = read_saved_ip()

    if curr_ip != saved_ip:
        for to_email in settings['to_email']:
            msg = MIMEText(
                f"Public IP address has changed from {saved_ip} to {curr_ip}"
            )
            msg['Subject'] = 'Alert - IP address has changed'
            msg['From'] = settings['from_email']
            msg['To'] = to_email

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
                server.login(settings['from_email'], settings['password'])
                server.sendmail(settings['from_email'],
                                to_email,
                                msg.as_string())

        persist_ip(curr_ip)
