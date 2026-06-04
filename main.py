import utils


def main():
    try:
        utils.logger.info("SCRIPT EXECUTION STARTED")
        print(f"Welcome to the DeleteTweets script!\n"
              f"What would you like to do?\n"
              f"1 - Delete one batch of tweets\n"
              f"2 - Delete multiple batches of tweets\n")
        while True:
            n = input("Please enter the command number: ")
            if utils.check_command(n, mode="Command"):
                n = int(n)
                break
            else:
                print("You entered an invalid command. Please try again.")
        if n == 2:
            while True:
                count = input("Enter the number of batches to delete: ")
                if utils.check_command(count, "Count"):
                    count = int(count)
                    break
                else:
                    print("You entered an invalid count. Please try again.")
        else:
            count = 1
        utils.logger.info(f"Deletion of tweets started. Count of batches: {count}")
        utils.clean_uc_cache()
        if not utils.os.path.exists("tweets.db"):
            utils.create_tweets_db()
        print("Start working...")
        start = utils.perf_counter()
        for i in range(count):
            if i > 0:
                if i % 3 == 0:
                    pause = utils.random.randint(180, 240)
                else:
                    pause = utils.random.randint(20, 40)
                print(f"Waiting for {pause} minutes between the butches...")
                utils.sleep(pause * 60 + utils.random.random())
            print(f"Start deletion of batch: {i + 1}")
            utils.delete_tweets()
            print(f"Batch {i + 1} deleted")
            end = utils.perf_counter()
            utils.logger.info(f"Batch of tweets deleted in {end - start}")
        utils.get_failed_tweets()
        utils.get_statistics()
    except utils.exceptions.PossibleCaptchaError:
        msg = (f"Possible CAPTCHA. Script execution stopped. Please pause deletion, "
                             f"log into Twitter manually (without the script), try deleting any tweet, "
                             f"and solve the CAPTCHA if it appears.")
        utils.logger.warning(msg)
        print(msg)
    except KeyboardInterrupt:
        utils.logger.info("Script terminated by user")
        print("\nScript terminated by user")
    except ConnectionResetError:
        utils.logger.error("Connection lost or script terminated by user")
        print("Connection lost or script terminated by user")
    except Exception as err:
        print(f"Script failed. Error: {err}")
        utils.logger.error(f"Script failed. Error: {err}", exc_info=True)
    finally:
        print("Finished!")
        utils.logger.info("SCRIPT EXECUTION FINISHED")
        utils.logger.info("-" * 30)


if __name__ == '__main__':
    main()
