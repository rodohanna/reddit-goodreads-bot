import praw
import re
import time
from uuid import uuid4
from goodreads import GoodReads
from db import DB
from formatter_factory import FormatterFactory


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

                formatter = FormatterFactory.for_subreddit(
                    subreddit_name=comment.subreddit.display_name,
                    book_info=book_info,
                    cleaned=cleaned,
                    book_suggestions=book_suggestions)

                # Build the formatted Reddit comment
                formatted_reddit_comment += formatter.format_link() + "\n\n"
                formatted_reddit_comment += formatter.format_header() + "\n\n"
                if self.__is_long_version(group) and formatter.supports_long_version():
                    formatted_reddit_comment += formatter.format_description() + "\n\n"

                formatted_reddit_comment += formatter.format_book_footer() + "\n\n"

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
