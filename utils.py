import json
import config


def split_json():
    try:
        n = 1
        file_number = 1
        temp_tweets = []
        folder = config.Path('tweets')
        folder.mkdir(exist_ok=True)
        with open(config.path, encoding='utf-8') as file:
            try:
                data = json.load(file)
                for tweet in data:
                    temp_tweets.append(tweet['tweet']['id'])
                    n += 1
                    if len(temp_tweets) == config.count:
                        with open(folder / f"tweets{file_number}.txt", mode='w', encoding='utf-8') as tweet_file:
                            tweet_file.write('\n'.join(line for line in temp_tweets))
                            temp_tweets.clear()
                        file_number += 1
                with open(folder / f"tweets{file_number}.txt", mode='w', encoding='utf-8') as tweet_file:
                    tweet_file.write('\n'.join(line for line in temp_tweets))
                    temp_tweets.clear()
                print("Success: File processed")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format")
    except FileNotFoundError as err:
        print(f"{err.strerror}: {err.filename}")
        print(f"Error: Invalid path or filename. Please check your config.")
