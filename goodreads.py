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

    def get_book_id(self,
                    book_title,
                    author=None,
                    depth=0,
                    original_book_title=None):
        author_name = self.search_author_by_name(author)

        print("book_title: %s" % book_title)

        print("author: %s, returned author: %s" % (author, author_name))

        query = book_title
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
            best_author_name_ratio = 0
            best_book_name_ratio = 0
            best_series_name_ratio = 0
            chosen_book = None
            if depth > 0 and original_book_title is not None:
                book_title = original_book_title
            for book in books:
                _author_name = book.find("author/name").text
                _book_title = book.find("title").text

                _book_title, series_name = self.__split_book_title_and_series(
                    _book_title)

                # some users will summon the bot with only the part of the title
                # before the ':'. i.e. Hello by Someone when the actual title is
                # Hello: World by Someone. This can confuse the bot. This check handles
                # that case.
                if book_title.lower() + ":" in _book_title.lower():
                    _book_title = _book_title.split(":")[0]
                    # print("updated book title %s" % _book_title)

                series_name_ratio = -1
                if series_name is not None:
                    series_name_ratio = fuzz.ratio(book_title.lower(),
                                                   series_name.lower())
                author_name_ratio = fuzz.ratio(author.lower(),
                                               _author_name.lower())
                book_name_ratio = fuzz.ratio(book_title.lower(),
                                             _book_title.lower())

                # print("looking at %s[%d] and %s[%d] and series %s[%d]" %
                #       (_author_name, author_name_ratio, _book_title,
                #        book_name_ratio, series_name, series_name_ratio))

                if author_name_ratio >= 90 and author_name_ratio >= best_author_name_ratio:
                    if book_name_ratio >= best_series_name_ratio and book_name_ratio > best_book_name_ratio:
                        # print("setting chosen book based on book")
                        best_author_name_ratio = author_name_ratio
                        best_book_name_ratio = book_name_ratio
                        chosen_book = book
                    if series_name_ratio >= best_book_name_ratio and series_name_ratio > best_series_name_ratio:
                        # print("setting chosen book based on book series")
                        best_author_name_ratio = author_name_ratio
                        best_series_name_ratio = series_name_ratio
                        chosen_book = book

            if chosen_book is not None:
                print("chosen book %s" % chosen_book.find("title").text)
                return chosen_book.find("id").text

        if depth == 0 and author is not None:
            return self.get_book_id(book_title + " " + author, author,
                                    depth + 1, book_title)

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

    def __split_book_title_and_series(self, book_title):
        series_match = None
        for series_match in re.finditer(r"\(([^)]+)\)", book_title):
            pass
        if series_match is not None:
            group = series_match.group()
            book_index_in_series = re.search("#\d.", group)

            if book_index_in_series is not None:
                series_name = group
                book_title = book_title.replace(series_name, "").strip()

                return (book_title, series_name.replace("(",
                                                        "").replace(")", ""))
        return (book_title, None)
