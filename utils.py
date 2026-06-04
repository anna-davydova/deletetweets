import sqlite3
import json
from pycparser.c_ast import Enum
import config
import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from time import sleep, perf_counter
import re
import random
import os
import shutil
import subprocess
from contextlib import contextmanager
from logger import logger
from collections import deque


class Button(Enum):
    MENU = "menu"
    DELETE = "delete"
    CONFIRM = "confirm"
    UNDO_REPOST = "undo_repost"
    CONFIRM_UNDO_REPOST = "confirm_undo_repost"


class TweetType(Enum):
    TWEET = "tweet"
    RETWEET = "retweet"


def check_command(n: str, mode: str):
    if mode == "Command":
        if n.strip() in ("1", "2"):
            return True
    elif mode == "Count":
        if n.strip().isdigit() and int(n) > 0:
            return True
    return False


def clean_uc_cache():
    """Clean cache undetected_chromedriver"""
    kill_chromedriver()
    cache_path = os.path.join(os.environ.get('APPDATA', ''), 'undetected_chromedriver')
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)
        logger.info("ChromeDriver cache has been successfully cleaned")


def kill_chromedriver():
    """Kill chromedriver process before clean cache"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'],
                       check=False,
                       capture_output=True)
    except Exception as err:
        logger.error(f"Failed to terminate ChromeDriver processes: {err}")
        raise


def get_chrome_version(path: config.Path) -> int:
    """Get Chrome version from .exe"""
    if not os.path.exists(path):
        logger.error("Invalid path to Chrome.exe. Check the config file.")
        raise FileNotFoundError(f"Invalid path to Chrome.exe. Check the config file.")
    try:
        cmd = f'powershell "(Get-Item \'{path}\').VersionInfo.ProductVersion"'
        version_full = subprocess.check_output(cmd, shell=True).decode().strip()
        return int(version_full.split('.')[0])
    except Exception as err:
        logger.error(f"Failed to get Chrome.exe version. Error: {err}")
        raise


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


@contextmanager
def chrome_driver(*args, **kwargs):
    driver = uc.Chrome(*args, **kwargs)
    try:
        yield driver
    finally:
        driver.quit()


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


def get_tweet_status(driver: uc.Chrome, url):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//article[@data-testid='tweet'] | //div[@data-testid='error-detail']"))
    )
    errors = driver.find_elements(By.XPATH, "//div[@data-testid='error-detail']")

    if errors:
        logger.warning(f"Tweet {url} NOT FOUND (Skipping)")
        return False
    else:
        logger.info(f"Tweet {url} IS ALIVE (Can be deleted)")
        return True


def scroll(driver: uc.Chrome):
    urls = [
        "https://x.com/home",
        "https://x.com/explore",
        "https://x.com/notifications"
    ]
    url = random.choice(urls)
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "main"))
    )
    sleep(random.uniform(1, 2))
    for i in range(random.randint(3, 7)):
        ActionChains(driver).scroll_by_amount(0, random.randint(15, 30)).perform()
        sleep(random.uniform(0.5, 1.5))


def get_type_selector(selector: str):
    if re.fullmatch(r"\[.+]", selector):
        return By.CSS_SELECTOR
    else:
        return By.XPATH


def click_button(driver: uc.Chrome, mode: str):
    button = None
    selectors = {
        Button.MENU: [
            "[aria-label='More']",
            "[data-testid='caret']"
        ],
        Button.DELETE: [
            "//div[@role='menuitem']//span[text()='Delete']",
            "//span[text()='Delete']",
            "[data-testid='delete']"
        ],
        Button.CONFIRM: [
            "[data-testid='confirmationSheetConfirm']",
            "//button//span[text()='Delete']"
        ],
        Button.UNDO_REPOST: [
            "[data-testid='unretweet']",
            "[aria-label*='Reposted']"
        ],
        Button.CONFIRM_UNDO_REPOST: [
            "[data-testid='unretweetConfirm']",
            "//div[@role='menuitem']//span[text()='Undo repost']"
        ]
    }
    button_exceptions = {
        Button.MENU: exceptions.MenuButtonNotFoundError,
        Button.DELETE: exceptions.DeleteButtonNotFoundError,
        Button.CONFIRM: exceptions.ConfirmButtonNotFoundError,
        Button.UNDO_REPOST: exceptions.UndoRepostButtonNotFoundError,
        Button.CONFIRM_UNDO_REPOST: exceptions.ConfirmUndoRepostButtonNotFoundError
    }

    for selector in selectors[mode]:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (get_type_selector(selector), selector)
                )
            )
            logger.info(f"{mode.title()} button found with selector {selector}")
            break
        except Exception:
            logger.error(f"{mode.title()} button not found with selector: {selector}")
    if not button:
        raise button_exceptions[mode](f"{mode.title()} button not found")
    sleep(random.uniform(1, 2))
    button.click()
    logger.info(f"{mode.title()} button clicked")
    sleep(random.uniform(1, 2))


def find_captcha(driver: uc.Chrome):
    # 1. Google reCAPTCHA
    recaptcha_iframes = driver.find_elements(By.XPATH, """
            //iframe[contains(@src, 'recaptcha') or contains(@src, 'google.com/recaptcha')]
        """)
    # 2. hCaptcha
    hcaptcha_iframes = driver.find_elements(By.XPATH, """
            //iframe[contains(@src, 'hcaptcha') or contains(@src, 'hcaptcha.com')]
        """)
    # 3. Custom Twitter Captcha
    custom_captcha = driver.find_elements(By.CSS_SELECTOR, """
            [role="dialog"],
            [aria-label*="Verify"],
            [aria-label*="human"],
            [aria-label*="solve"],
            [aria-label*="puzzle"]
        """)
    return recaptcha_iframes or hcaptcha_iframes or custom_captcha


def delete_tweet(driver: uc.Chrome, url: str):
    try:
        logger.info(f"Starting deletion for tweet: {url}")
        click_button(driver, Button.MENU)
        click_button(driver, Button.DELETE)
        if find_captcha(driver):
            raise exceptions.PossibleCaptchaError
        click_button(driver, Button.CONFIRM)
        logger.info(f"Tweet {url} deleted")
        return True
    except exceptions.PossibleCaptchaError:
        raise
    except exceptions.ButtonError as err:
        logger.error(f"Failed to delete tweet: {url}. Error: {err}")
        return False
    except Exception:
        logger.error(f"Failed to delete tweet: {url}", exc_info=True)
        print(f"Failed to delete tweet: {url}")
        return False


def delete_retweet(driver: uc.Chrome, url: str):
    try:
        logger.info(f"Starting deletion for retweet: {url}")
        click_button(driver, Button.UNDO_REPOST)
        if find_captcha(driver):
            raise exceptions.PossibleCaptchaError
        click_button(driver, Button.CONFIRM_UNDO_REPOST)
        logger.info(f"Retweet {url} deleted")
        return True
    except exceptions.PossibleCaptchaError:
        raise
    except exceptions.ButtonError as err:
        logger.error(f"Failed to delete retweet: {url}. Error: {err}")
        return False
    except Exception:
        logger.error(f"Failed to delete retweet: {url}", exc_info=True)
        print(f"Failed to delete retweet: {url}")
        return False


def delete_tweets() -> None:
    queue = deque([True] * 5, maxlen=5)
    tweet_types = {
        TweetType.TWEET: delete_tweet,
        TweetType.RETWEET: delete_retweet
    }
    options = uc.ChromeOptions()
    options.binary_location = str(config.chrome_path)
    options.add_argument(f"--user-data-dir={str(config.profile_path)}")
    chrome_version = get_chrome_version(config.chrome_path) if config.version is None else config.version
    with init_db() as conn:
        cur = conn.cursor()
        count = random.randint(20, 25)
        cur.execute("""
                        SELECT id, type
                        FROM tweets
                        WHERE status IS NULL
                        LIMIT (?);
                    """, (count,))
        tweets = cur.fetchall()
        if tweets:
            print(f"Selected tweets to delete: {count}")
            logger.info(f"Selected tweets to delete: {count}")
            with chrome_driver(options=options, version_main=chrome_version) as driver:
                driver.set_page_load_timeout(30)
                for tweet in tweets:
                    waiting = random.uniform(5, 10)
                    url = f"https://x.com/user/status/{tweet["id"]}"
                    logger.info(f"Start checking tweet: {url}")
                    try:
                        driver.get(url)
                        if get_tweet_status(driver, url):
                            result = tweet_types[tweet["type"]](driver, url)
                            queue.append(result)
                            if not any(queue):
                                raise exceptions.PossibleCaptchaError
                            status = 'Deleted' if result else 'Failed'
                        else:
                            status = "Not found"
                        try:
                            with transaction(conn):
                                cur.execute("""
                                                UPDATE tweets
                                                SET status = (?)
                                                WHERE id = (?)
                                            """, (status, tweet["id"]))
                        except Exception as err:
                            logger.error(f"Failed to save tweet {url} to the database. Error: {err}")
                        sleep(waiting)
                        if random.random() < 0.15:
                            scroll(driver)
                    except exceptions.PossibleCaptchaError:
                        raise
                    except TimeoutException:
                        logger.error(f"Timeout or unknown page for URL: {url}")
                        sleep(waiting)
                scroll(driver)
        else:
            print("All tweets deleted")
            logger.info("All tweets deleted")
