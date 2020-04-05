import argparse


def get_parser():
    parser = argparse.ArgumentParser(description='Checks ip address and sends an email'
                                                 ' when it changes. To check ip, run '
                                                 ' with no command line arguments.')
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