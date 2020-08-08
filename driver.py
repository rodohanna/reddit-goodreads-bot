from bot import Bot
from configparser import ConfigParser

config = ConfigParser()
config.read('praw.ini')
config = config["DEFAULT"]

# This is a (temporary) hacky way of keeping the bot alive if it fails.
# If we fail more than 50 times just quit.

failures = 0
while True:
    try:
        bot = Bot()
        bot.listen_to_subreddit(config["subreddit"])
    except Exception as e:
        print("The bot died: ", e)
        failures += 1
