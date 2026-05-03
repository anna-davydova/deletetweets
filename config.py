import configparser
from pathlib import Path
import os

config_name = r'configuration.ini'

try:
    if not os.path.exists(config_name):
        raise FileNotFoundError(f'Configuration file not found: {config_name}')

    config = configparser.ConfigParser()
    config.read(config_name, encoding='utf-8')
    try:
        path = Path(config['data']['path'])
        count = int(config['data']['count_tweets'])
    except KeyError as err:
        print(f"Missing required configuration key: {err}")
except FileNotFoundError as err:
    print(err)
