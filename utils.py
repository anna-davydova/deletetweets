import json
import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from time import sleep, perf_counter
import re
import random
import os
import shutil
import subprocess


def clean_uc_cache():
    """Clean cache undetected_chromedriver"""
    kill_chromedriver()
    cache_path = os.path.join(os.environ.get('APPDATA', ''), 'undetected_chromedriver')
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)


def kill_chromedriver():
    """Kill chromedriver process before clean cache"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'],
                       check=False,
                       capture_output=True)
    except Exception as err:
        print(f"Failed to terminate ChromeDriver processes: {err}")


def get_file_version(path: config.Path) -> int | None:
    """Get Chrome version from .exe"""
    if not os.path.exists(path):
        return None
    try:
        cmd = f'powershell "(Get-Item \'{path}\').VersionInfo.ProductVersion"'
        version_full = subprocess.check_output(cmd, shell=True).decode().strip()
        return int(version_full.split('.')[0])
    except Exception:
        return None


def get_tweet_type(full_text: str) -> str:
    if re.fullmatch(r"RT @.+", full_text):
        return "retweet"
    return "tweet"


def split_json(folder: config.Path) -> None:
    try:
        count = random.randint(20, 30)
        n = 1
        file_number = 1
        temp_tweets = []
        folder.mkdir(exist_ok=True)
        with open(config.path, encoding="utf-8") as file:
            try:
                data = json.load(file)
                for tweet in data:
                    dict_tweet = {"id": n,
                                  "tweet_id": tweet["tweet"]["id"],
                                  "type": get_tweet_type(tweet["tweet"]["full_text"]),
                                  "status": None}
                    temp_tweets.append(dict_tweet)
                    n += 1
                    if len(temp_tweets) == count:
                        with open(folder / f"tweets{file_number}.json", mode="w", encoding="utf-8") as tweet_file:
                            json.dump(temp_tweets, tweet_file, indent=2)
                            temp_tweets.clear()
                            count = random.randint(20, 30)
                        file_number += 1
                with open(folder / f"tweets{file_number}.json", mode="w", encoding="utf-8") as tweet_file:
                    json.dump(temp_tweets, tweet_file, indent=2)
                    temp_tweets.clear()
                print("Success: File processed")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format")
    except FileNotFoundError as err:
        print(f"{err.strerror}: {err.filename}")
        print(f"Error: Invalid path or filename. Please check your config.")


def get_next_file() -> config.Path:
    log_file = config.Path("short.log")
    if not log_file.exists():
        next_file = config.Path("tweets1.json")
    else:
        with open("short.log", encoding="utf-8") as file:
            data = file.readlines()
            if data:
                number = int(re.search(r"\d+", data[-1].strip()).group())
                next_file = config.Path(f"tweets{number + 1}.json")
            else:
                next_file = config.Path("tweets1.json")
    return next_file


def delete_tweets(folder: config.Path) -> None:
    file_name = get_next_file()
    options = uc.ChromeOptions()
    options.binary_location = str(config.chrome_path)
    options.add_argument(f"--user-data-dir={str(config.profile_path)}")
    chrome_version = get_file_version(config.chrome_path)
    with (open(folder / file_name, encoding='utf-8') as file,
          open('full.log', mode='a', encoding='utf-8') as full_log,
          open('short.log', mode='a', encoding='utf-8') as shot_log,
          uc.Chrome(options=options,
                    version_main=chrome_version) as driver):
        for tweet_id in file:
            waiting = 5 + random.random() * random.randint(5, 10)
            url = f"https://x.com/user/status/{tweet_id.strip()}"
            print(f"File: {file_name}. Checking: {url}", file=full_log)
            print(f"File: {file_name}. Checking: {url}")
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//article[@data-testid='tweet'] | //div[@data-testid='error-detail']"))
                )
                errors = driver.find_elements(By.XPATH, "//div[@data-testid='error-detail']")

                if errors:
                    print(f"File: {file_name}. Result: Tweet {tweet_id} NOT FOUND (Skipping)", file=full_log)
                    print(f"File: {file_name}. Result: Tweet {tweet_id} NOT FOUND (Skipping)")
                else:
                    print(f"File: {file_name}. Result: Tweet {tweet_id} IS ALIVE (Can be deleted)", file=full_log)
                    print(f"File: {file_name}. Result: Tweet {tweet_id} IS ALIVE (Can be deleted)")
                sleep(waiting)
            except TimeoutException:
                print(f"File: {file_name}. Result: Timeout or unknown page state for {tweet_id}", file=full_log)
                print(f"File: {file_name}. Result: Timeout or unknown page state for {tweet_id}")
                sleep(waiting)
        print(f"File {file_name} is complete", file=shot_log)
        print(f"File {file_name} is complete")
