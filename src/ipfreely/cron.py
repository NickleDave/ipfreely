"""module for functions dealing with cron jobs.
adapted from https://github.com/monklof/deploycron
under MIT license (https://github.com/monklof/deploycron/blob/master/LICENSE)
"""
import os
import subprocess
import sys


def _runcmd(cmd, input=None):
    '''run shell command and return the a tuple of the cmd's return code, std error and std out
    WARN: DO NOT RUN COMMANDS THAT NEED TO INTERACT WITH STDIN WITHOUT SPECIFY INPUT,
    (eg cat), IT WILL NEVER TERMINATE.'''
    if input is not None:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)
    else:
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)

    stdoutdata, stderrdata = p.communicate(input)
    return p.returncode, stderrdata, stdoutdata


def add_cron_lines(filename="",
                   cron_lines="", override=False):
    """add lines to a crontab.

    filename : str
        file contains crontab, one crontab for a line
    cron_lines : str
        string that contains lines for crontab
    override : bool
        if True, override the originak crontab

    Will not remove other crontabs installed in the system if not specified
    as override. It just merge the new one with the existing one.
    If you provide `filename`, then will install the crontabs in that file
    otherwise install crontabs specified in content
    """
    if not filename and not cron_lines:
        raise ValueError("either filename or cron_lines must be specified")

    if filename:
        try:
            with open(filename, 'r') as f:
                cron_lines = f.read().split("\n")
        except Exception as e:
            raise ValueError("cannot open the file: %s" % str(e))

    if override:
        cron_lines = ""

    else:
        # currently installed crontabs
        retcode, err, installed_cron_lines = _runcmd("crontab -l")
        if retcode != 0 and 'no crontab for' not in err.decode('ascii'):
            raise OSError("crontab not supported in your system")
        installed_cron_lines = installed_cron_lines.decode('ascii')
        # take off the last newline so we can append (with lines that start with a newline)
        cron_lines_out = installed_cron_lines.rstrip("\n")

    current_cron_lines = installed_cron_lines.split("\n")
    for cron_line in cron_lines:
        if cron_line and cron_line not in current_cron_lines:
            if not cron_lines_out:  # if an empty list
                cron_lines_out += cron_line
            else:
                cron_lines_out += "\n%s" % cron_line
    if cron_lines_out:  # add final newline
        cron_lines_out += "\n"

    cron_lines_out = cron_lines_out.encode(sys.getfilesystemencoding())
    retcode, err, out = _runcmd("crontab", cron_lines_out)
    if retcode != 0:
        raise ValueError("failed to install crontab, check if crontab is valid")
