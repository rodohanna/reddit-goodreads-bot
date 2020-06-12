from bot import Bot

# This is a (temporary) hacky way of keeping the bot alive if it fails.
# If we fail more than 50 times just quit.

failures = 0
while True:
    try:
        if failures > 50:
            print("The bot has failed too many times.. Killing the bot :(")
            exit()
        bot = Bot()
        bot.listen_to_subreddit("test")
    except Exception as e:
        print("The bot died: ", e)
        failures += 1
