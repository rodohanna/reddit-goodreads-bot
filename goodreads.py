import requests
import re
import time
from xml.etree import ElementTree
from configparser import ConfigParser
from fuzzywuzzy import fuzz

config = ConfigParser()
config.read('praw.ini')
config = config["DEFAULT"]


class GoodReads:
    api_method_to_last_called_unix = {"show": 0, "search": 0, "author": 0}

    def __init__(self):
        self.api_key = config["goodreads_key"]
        return

    # GoodReads mandates that we do not request a given API method more than once
    # a second. This function keeps us in line with GoodReads' API guidelines.
    def sleep_if_needed(self, now, api_method):
        last_api_call_unix = self.api_method_to_last_called_unix[api_method]
        if last_api_call_unix is not 0:
            seconds_since_last_api_call = now - last_api_call_unix

            print("[%s] seconds since last API call" % api_method,
                  seconds_since_last_api_call)

            time_to_sleep = 1 - seconds_since_last_api_call
            if time_to_sleep > 0:
                print("sleeping for ", time_to_sleep)
                time.sleep(time_to_sleep)

    def search_author_by_name(self, name):
        if name is None:
            return None

        now = time.time()

        self.sleep_if_needed(now, "author")

        params = [('key', self.api_key)]
        response = requests.get("https://www.goodreads.com/api/author_url/%s" %
                                name,
                                params=params)
        self.api_method_to_last_called_unix["author"] = time.time()

        if response.status_code == 404:
            return None

        tree = ElementTree.fromstring(response.content)
        name = tree.find("author/name")
        if name is None:
            return None

        return name.text

    def get_book_id(self, book, author=None):
        author_name = self.search_author_by_name(author)

        print("author: %s, returned author: %s" % (author, author_name))

        query = book
        is_valid_author_name = False

        if author is not None and author_name is not None:
            ratio = fuzz.ratio(author.lower(), author_name.lower())
            print("Author name ratio: ", ratio)
            if ratio < 90:  # we are pretty sure the author name is actually par of the book title
                query += " by " + author
            else:
                is_valid_author_name = True

        now = time.time()
        self.sleep_if_needed(now, "search")

        params = [('key', self.api_key), ('q', query)]
        response = requests.get("https://www.goodreads.com/search/index.xml",
                                params=params)
        self.api_method_to_last_called_unix["search"] = time.time()

        if response.status_code == 404:
            return None

        tree = ElementTree.fromstring(response.content)
        books = tree.findall("search/results/work/best_book")
        if books is None or len(books) == 0:
            return None

        if is_valid_author_name:
            for book in books:
                author_name = book.find("author/name").text
                ratio = fuzz.ratio(author.lower(), author_name.lower())
                if ratio >= 90:
                    return book.find("id").text

        return books[0].find("id").text

    def get_book_info(self, book_id):
        now = time.time()
        self.sleep_if_needed(now, "show")

        params = [('key', self.api_key)]
        response = requests.get("https://www.goodreads.com/book/show/%s.xml" %
                                book_id,
                                params=params)
        self.api_method_to_last_called_unix["show"] = time.time()

        if response.status_code == 404:
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
