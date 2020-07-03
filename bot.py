import praw
import re
import time
from uuid import uuid4
from goodreads import GoodReads
from db import DB


class Bot:
    def __init__(self):
        self.reddit = praw.Reddit()
        self.goodreads = GoodReads()
        self.db = DB()

        self.db.create_tables()

    def listen_to_subreddit(self, name):
        for comment in self.reddit.subreddit(name).stream.comments():
            print("comment: ", comment.body)
            comment_invocations = self.db.count_comment_invocations(comment.id)
            if comment_invocations > 0:
                continue
            submission = comment.submission
            formatted_reddit_comment = ""
            for m in re.finditer('\{\{([^}]+)\}\}|\{([^}]+)\}', comment.body):
                # Clean the Input
                group = m.group()
                cleaned = self.__clean_group(group)

                print("group: ", group)
                print("cleaned: ", cleaned)

                # Extract the book and author, then retrieve the data from GoodReads
                book, author = self.__extract_book_and_author(cleaned)
                book_id = self.goodreads.get_book_id(book, author)
                book_info = self.goodreads.get_book_info(book_id)

                print("book_info", book_info)
                if book_info is None:
                    continue

                # Save the book and summons for our stats
                book = (book_id, book_info["title"], book_info["url"],
                        int(time.time()))
                invocation = (str(uuid4()), book_id, comment.id, submission.id,
                              "", comment.permalink, int(time.time()))
                self.db.save_book(book)
                self.db.save_invocation(invocation)

                book_suggestions = self.db.count_book_requests(book_id)

                # Build the formatted Reddit comment
                formatted_reddit_comment += self.__format_link(
                    book_info) + "\n\n"
                formatted_reddit_comment += self.__format_header(
                    cleaned, book_info) + "\n\n"
                if self.__is_long_version(group):
                    formatted_reddit_comment += self.__format_description(
                        book_info) + "\n\n"

                formatted_reddit_comment += self.__format_book_footer(
                    book_suggestions) + "\n\n"

            if len(formatted_reddit_comment) > 0:
                # We are responding to a comment, so let's save the post
                post = (submission.id, submission.title, submission.url)
                self.db.save_post(post)

                formatted_reddit_comment += "***\n\n"

                invocations = self.db.count_invocations()
                formatted_reddit_comment += self.__make_footer(invocations)
                comment.reply(formatted_reddit_comment)

    def __extract_book_and_author(self, match):
        book, *author = match.lower().rsplit("by", 1)
        book = book.strip()
        author = author[0].strip() if author else None

        return (book, author)

    def __format_link(self, book_info):
        title = book_info["title"]
        url = book_info["url"]

        return "[**%s**](%s)" % (title, url)

    def __format_description(self, book_info):
        description = book_info["description"]
        if description is None:
            return ""
        description = re.sub('<.*?>', '', description.replace("<br />", "\n"))

        chunks = [">" + chunk for chunk in description.split("\n")]

        return "\n".join(chunks)

    def __format_header(self, search_query, book_info):
        pages = book_info["num_pages"]
        year = book_info["pub_year"]
        shelves = ", ".join(book_info["shelves"])
        authors = ", ".join(book_info["authors"])
        search_link = "https://www.goodreads.com/search?q=%s&search_type=books" % search_query

        return "^(By: %s | %s pages | Published: %s | Popular Shelves: %s | )[^(Search \"%s\")](%s)" % (
            authors, pages or "?", year
            or "?", shelves, search_query, search_link)

    def __format_book_footer(self, book_suggestions):
        s = "s" if book_suggestions > 1 else ""
        return "^(This book has been suggested %s time%s)" % (book_suggestions,
                                                              s)

    def __is_long_version(self, group):
        return (group.count("{") + group.count("}")) == 4

    def __is_short_version(self, group):
        return (group.count("{") + group.count("}")) == 2

    def __clean_group(self, group):
        return group.replace("{", "").replace("}", "").replace("*", "")

    def __make_footer(self, suggestions):
        s = "s" if suggestions > 1 else ""
        return "^(%s book%s suggested | )^(Bug? DM me! | )[^(Source)](https://github.com/rodohanna/reddit-goodreads-bot)" % (
            suggestions, s)
