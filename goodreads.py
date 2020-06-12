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
        popular_shelves = book.find("popular_shelves")
        authors = book.find("authors")

        shelf_list = []
        for shelf in popular_shelves:
            shelf_name = shelf.get("name")
            if shelf_name == "to-read" or shelf_name == "currently-reading" or shelf_name == "favorites":
                continue
            shelf_list.append(shelf_name)

        author_list = []
        for author in authors:
            author_name = author.find("name").text
            author_list.append(author_name)

        shelves = shelf_list[:5]
        title = book.find("title").text
        url = book.find("url").text
        description = book.find("description").text
        num_pages = book.find("num_pages").text
        pub_year = book.find("work/original_publication_year").text

        return {
            "url": url,
            "num_pages": num_pages,
            "pub_year": pub_year,
            "shelves": shelves,
            "authors": author_list,
            "title": title,
            "description": description
        }
