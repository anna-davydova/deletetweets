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
        path = Path(config['data']['json_path'])
        count = int(config['data']['count_tweets'])
        chrome_path = Path(config['data']['chrome_exe_path'])
        profile_path = Path(config['data']['chrome_user_profile_path'])
    except KeyError as err:
        print(f"Missing required configuration key: {err}")
except FileNotFoundError as err:
    print(err)
