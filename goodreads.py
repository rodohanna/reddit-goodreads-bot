import requests
import re
import time
from xml.etree import ElementTree
from configparser import ConfigParser

config = ConfigParser()
config.read('praw.ini')
config = config["DEFAULT"]


class GoodReads:
    last_api_call_unix = 0

    def __init__(self):
        self.api_key = config["goodreads_key"]
        return

    def get_book_info(self, title, author=None, depth=0):
        now = time.time()

        if self.last_api_call_unix is not 0:
            seconds_since_last_api_call = now - self.last_api_call_unix

            print("seconds since last API call", seconds_since_last_api_call)

            time_to_sleep = 1 - seconds_since_last_api_call
            if time_to_sleep > 0:
                print("sleeping for ", time_to_sleep)
                time.sleep(time_to_sleep)

        params = [('key', self.api_key), ('title', title), ('author', author)]
        response = requests.get("https://www.goodreads.com/book/title.xml",
                                params=params)
        self.last_api_call_unix = time.time()

        if response.status_code == 404:
            if author != None and depth == 0:
                print("Not found.. trying again.")
                return self.get_book_info(title, None, depth + 1)
            else:
                print("Not found again.. returning None")
                return None

        tree = ElementTree.fromstring(response.content)
        book = tree.find("book")
        url = book.find("url").text
        description = book.find("description").text

        return {"url": url, "description": description}
