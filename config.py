import configparser
from pathlib import Path
import os
from datetime import datetime
from sys import exit
from logger import logger

config_name = r'configuration.ini'

logger.info(f"READING CONFIGURATION FILE STARTED")
if not os.path.exists(config_name):
    logger.error(f"Configuration file not found: {config_name}")
    print(f"Script execution aborted. Configuration file not found: {config_name}. Please check your configuration file")
    exit(1)

config = configparser.ConfigParser()
config.read(config_name, encoding='utf-8')
try:
    path = Path(config['data']['json_path'])
    chrome_path = Path(config['data']['chrome_exe_path'])
    profile_path = Path(config['data']['chrome_user_profile_path'])
    version = int(config['data']['version']) if config['data']['version'].isdigit() else None
    match (config['tweet_parameters']['start_date'], config['tweet_parameters']['end_date']):
        case ('None', 'None'):
            start_date = None
            end_date = None
        case _:
            try:
                start_date = datetime.fromisoformat(config['tweet_parameters']['start_date']).date()
                end_date = datetime.fromisoformat(config['tweet_parameters']['end_date']).date()
            except ValueError:
                logger.error("Script execution aborted. Invalid format for start_date or end_date.")
                print("Script execution aborted. Invalid format for start_date or end_date. Please check your configuration file")
                exit(1)
    logger.info(f"READING CONFIGURATION FILE SUCCESSFULLY FINISHED")
except KeyError as err:
    logger.error(f"Missing required configuration key: {err}")
    print(f"Missing required configuration key: {err}. Please check your configuration file")
    exit(1)
