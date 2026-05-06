import utils


def main():
    try:
        utils.clean_uc_cache()
        folder = utils.config.Path('tweets')
        if not folder.exists() or not any(folder.glob('tweets[0-9].txt')):
            utils.split_json(folder)
        utils.delete_tweets(folder)
        print(utils.perf_counter() - start)
    except Exception as err:
        print(err)


start = utils.perf_counter()
if __name__ == '__main__':
    main()
