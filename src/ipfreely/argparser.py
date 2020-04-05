import argparse


def get_parser():
    """creates argparser, used by __main__.main function"""
    parser = argparse.ArgumentParser(description='Checks ip address and sends an email'
                                                 ' when it changes. To check ip, run '
                                                 ' with no command line arguments.')

    subparser = parser.add_subparsers(title='commands',
                                      description="commands accepted by the ipfreely command-line interface",
                                      dest='command',)
    send_parser = subparser.add_parser('send', help='send an email with current ip, using current config')
    check_parser = subparser.add_parser('check', help='check whether ip has changed, and if so send an email')
    activate_parser = subparser.add_parser('activate', help='activate ipfreely to run as a cron job')
    deactivate_parser = subparser.add_parser('deactivate', help='takes ipfreely off cron job list')

    config_subparser = subparser.add_parser('config',
                                            help='configure ipfreely settings')

    config_subparser.add_argument('-f', '--from',
                                  help='email address from which to send alerts when ip address changes')
    config_subparser.add_argument('-p', '--password',
                                  help='password for \'from\' email address. Don\'t use one you care about.')
    config_subparser.add_argument('-t', '--to',
                                  help='email address to which alert emails should be sent')
    config_subparser.add_argument('-n', '--name',
                                  help='name for this computer (in case you have ipfreely running on'
                                       ' multiple computers')

    return parser
