import sqlite3
import json
import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from time import sleep
import re
import random
import os
import shutil
import subprocess
from contextlib import contextmanager


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


def get_chrome_version(path: config.Path) -> int | None:
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


def init_db(db_name="tweets.db"):
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def create_tweets_db():
    with init_db() as conn:
        cur = conn.cursor()
        cur.execute("""
                        CREATE TABLE IF NOT EXISTS tweets (
                            id TEXT PRIMARY KEY,
                            type TEXT,
                            status TEXT DEFAULT NULL
                        )
                    """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON tweets(status)")
        try:
            with open(config.path, encoding="utf-8") as file:
                data = json.load(file)
                insert_tweets = []
                for tweet in data:
                    insert_tweets.append((tweet["tweet"]["id"], get_tweet_type(tweet["tweet"]["full_text"])))
                cur.executemany(
                    "INSERT OR IGNORE INTO tweets (id, type) VALUES (?, ?)",
                    insert_tweets
                )
        except FileNotFoundError as err:
            print(f"{err.strerror}: {err.filename}")
            print(f"Error: Invalid path or filename. Please check your config.")


def delete_tweets() -> None:
    options = uc.ChromeOptions()
    options.binary_location = str(config.chrome_path)
    options.add_argument(f"--user-data-dir={str(config.profile_path)}")
    chrome_version = get_chrome_version(config.chrome_path)
    with init_db() as conn:
        cur = conn.cursor()
        cur.execute("""
                        SELECT id, type
                        FROM tweets
                        WHERE status IS NULL
                        LIMIT (?);
                    """, (random.randint(3, 5),))
        tweets = cur.fetchall()
        if tweets:
            with uc.Chrome(options=options, version_main=chrome_version) as driver:
                for tweet in tweets:
                    waiting = random.uniform(5, 10)
                    url = f"https://x.com/user/status/{tweet["id"]}"
                    driver.get(url)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//article[@data-testid='tweet'] | //div[@data-testid='error-detail']"))
                        )
                        errors = driver.find_elements(By.XPATH, "//div[@data-testid='error-detail']")

                        if errors:
                            print(f"Result: Tweet {tweet["id"]} NOT FOUND (Skipping)")
                            status = 'not found'
                        else:
                            print(f"Result: Tweet {tweet["id"]} IS ALIVE (Can be deleted)")
                            status = 'deleted'
                        try:
                            with transaction(conn):
                                cur.execute("""
                                                UPDATE tweets
                                                SET status = (?)
                                                WHERE id = (?)
                                            """, (status, tweet["id"]))
                        except Exception as err:
                            print(f"Failed to save tweet with ID {tweet["id"]} to the database: {err}")
                        sleep(waiting)
                    except TimeoutException:
                        print(f"Result: Timeout or unknown page state for {tweet["id"]}")
                        sleep(waiting)
        else:
            print("All tweets have been deleted")
