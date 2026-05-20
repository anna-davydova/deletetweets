import utils


def main():
    try:
        utils.clean_uc_cache()
        if not utils.os.path.exists("tweets.db"):
            utils.create_tweets_db()
        utils.delete_tweets()
    except Exception as err:
        print(f"Script failed. Error: {err}")
        utils.logger.error(f"Script failed. Error: {err}")


if __name__ == '__main__':
    main()
