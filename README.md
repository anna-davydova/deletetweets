[English](README.md) | [Russian](README_ru.md)

## Description

You can use this script to delete tweets from your X profile (formerly Twitter).
The X API has been fully paid since 2026, so this script uses automation via Selenium.
Deleting tweets will take some time, but it's completely free. You don't need to share your login and password, everything is done only on your PC.

You log in to your X account, then the script on your PC automatically opens the browser, follows the links to the tweets, and deletes them.

The script works on Windows 10 and 11, but only with the Google Chrome Portable browser.

## Disclaimer

Use the script at your own risk. I'm not responsible for your account. If you are unsure, it is better not to use it at all.

The script doesn't guarantee 100% deletion of tweets, but it should successfully delete tweets from your X archive. 
Links to tweets that the script cannot find will be added to the `not_found_tweets.txt` file.

I don't recommend changing the following parameters in the code:

* Number of tweets to delete
* Time delays between script actions

I have personally tested the current parameters. With these parameters, I successfully deleted around 5,800 tweets. 
Changing them may lead to unexpected issues with your account.

## Features

This script simulates human-like behavior:

* Deletes tweets in batches of 20–25 at a time
* Adds random delays between button clicks and tweet deletions
* Randomly opens pages and scrolls down a bit between tweet deletions
* Stores statistics in an SQLite database
* Allows filtering by a specific date range

## Installation

1. Request your tweet archive from X. To do this, go to X and navigate to "More" -> 
"Settings and privacy" -> "Your account" -> "Download an archive of your data".
The archive takes about 2 days to prepare.
2. Download the archive and extract it. In the `data` folder, find the `tweets.js` file. 
Open it with a text editor and remove the `window.YTD.tweets.part0 = ` line before the opening square bracket, 
then save the file as a **JSON** file (e.g., `tweets.json`).

![twitter_json_1.png](docs/imgs/twitter_json_1.png)
![twitter_json_2.png](docs/imgs/twitter_json_2.png)

3. Download or clone the repository.
4. Install [Python](https://www.python.org/downloads/ "Python") 3.12 or higher. 
Make sure to check the `Add python.exe to PATH` box.
5. Install the [Google Chrome Portable](https://portableapps.com/apps/internet/google_chrome_portable "Google Chrome Portable") browser. **The script doesn't work with regular Chrome!**
6. Open Google Chrome Portable, log in to the browser on X (https://x.com/), accept all cookies. Crucial: switch the language in X settings to English: "More" -> "Settings and privacy" -> "Accessibility, display, and languages", then close the browser.
7. Install uv:
```
winget install astral-sh.uv
```
8. Change directory to the script directory:
```
cd <path_to_directory>
```
9. Install dependencies:
```
uv sync
```
10. Rename `configuration.ini.example` to `configuration.ini` and fill in the following fields:

* **json_path** - path to the JSON file from step 2
* **chrome_exe_path** - path to chrome.exe, for example: `D:\PortableApps\GoogleChromePortableNew\App\Chrome-bin\chrome.exe`
* **chrome_user_profile_path** - path to the Chrome Portable profile, for example: `D:\PortableApps\GoogleChromePortableNew\Data\profile`
* **version** - leave version as `None` for automatic version detection. 
If you encounter browser version-related errors, specify the first number of the Chrome version in this field 
(e.g., enter `151` if your Chrome version is `151.0.7922.72`)

Leave both of the following fields as `None` if you want to delete all your tweets, or specify the start and end dates 
of the time period in ISO format (`YYYY-MM-DD`) in both fields. For example: `2026-01-01` and `2026-12-31`

* **start_date** - start date of the time period
* **end_date** - end date of the time period

11. Run the script:
```
uv run main.py
```

## Operation Modes

### 1. Delete one batch of tweets
The script deletes a single batch of tweets and then exits. 
Deleting one batch takes about 5-10 minutes.

### 2. Delete multiple batches of tweets
In this mode, you can specify the number of batches to delete. 
After each batch, the browser closes and the script shows the start time for the next one.  
**Don't close the script terminal.**

**Delay Algorithm:**
*   **First 3 batches:** a random delay of 20-40 minutes between each batch.
*   **After the 3rd batch:** a long delay of 120-240 minutes.
*   The cycle then repeats.

## Notes and Recommendations

*   The script works only with tweets included in your X archive.
*   If you plan to unfollow accounts, do it after you finish deleting all necessary tweets.
*   Make sure your browser is closed before starting the script. The script opens the browser automatically.
*   While a batch is being deleted, don't use your PC, don't open the browser, 
and don't log into X from other devices.
*   The browser might not open immediately. This is normal, just wait a moment.
*   Don't delete too much at once.  If you delete tweets batch by batch, take 20–40 minute breaks. 
After deleting several batches, take a long break for a few hours.
*   Don't try to delete everything in one day. Keep to 100–200 tweets per day with intervals. 
Don't run the script 24/7.
*   If the script stops loading pages or exits with a CAPTCHA warning, close the script, 
open your browser manually, log into X, and try to delete any tweet by hand. Then take a break.
*   To change the date range for deletion, delete or move the `tweets.db` file from the script directory, 
update the dates in `configuration.ini`, and run the script again.