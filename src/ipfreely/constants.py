from pathlib import Path

CONFIG_ROOT = Path('~/.ipfreely').expanduser()

SETTINGS_FILENAME = 'settings.json'
SETTINGS_PATH = CONFIG_ROOT.joinpath(SETTINGS_FILENAME)

CURRENT_IP_ADDRESS_FILENAME = 'current_ip_address.txt'
CURRENT_IP_ADDRESS_PATH = CONFIG_ROOT.joinpath(CURRENT_IP_ADDRESS_FILENAME)