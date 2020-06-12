import praw
import re
import time
from uuid import uuid4
from goodreads import GoodReads
from db import DB

reddit = praw.Reddit()
goodreads = GoodReads()
cleanr = re.compile('<.*?>')
search_link = "https://www.goodreads.com/search?q=%s&search_type=books&search[field]=title"

db = DB()
db.create_tables()


def get_book_and_author(match):
    book, *author = match.lower().rsplit("by", 1)
    book = book.strip()
    author = author[0].strip() if author else None

    return (book, author)


def format_link(book_info):
    title = book_info["title"]
    url = book_info["url"]

    return "[**%s**](%s)" % (title, url)


def format_description(book_info):
    description = book_info["description"]
    if description is None:
        return ""
    description = re.sub(cleanr, '', description.replace("<br />", "\n"))

    chunks = [">" + chunk for chunk in description.split("\n")]

    return "\n".join(chunks)


def format_disclaimer(book):
    return "^(I'm a bot so it's possible I got the book wrong. Click on this link to search GoodReads for) [%s](%s)\n" % (
        book, search_link % book)


def format_header(search_query, book_info):
    pages = book_info["num_pages"]
    year = book_info["pub_year"]
    shelves = ", ".join(book_info["shelves"])
    authors = ", ".join(book_info["authors"])

    return "^(By: %s | %s pages | Published: %s | Popular Shelves: %s | )[^(Search \"%s\")](%s)" % (
        authors, pages, year, shelves, search_query,
        search_link % search_query)


def is_long_version(group):
    return (group.count("{") + group.count("}")) == 4


def is_short_version(group):
    return (group.count("{") + group.count("}")) == 2


def clean_group(group):
    return group.replace("{", "").replace("}", "").replace("*", "")


def make_footer():
    return "^(Bug? DM me! | )[^(Source)](https://github.com/rodohanna/reddit-goodreads-bot)"


for comment in reddit.subreddit("test").stream.comments(skip_existing=True):
    print("comment: ", comment.body)
    submission = comment.submission
    formatted_reddit_comment = ""
    for m in re.finditer('\{\{([^}]+)\}\}|\{([^}]+)\}', comment.body):
        # Clean the Input
        group = m.group()
        cleaned = clean_group(group)

        print("group: ", group)
        print("cleaned: ", cleaned)

        # Extract the book and author, then retrieve the data from GoodReads
        book, author = get_book_and_author(cleaned)
        book_id = goodreads.get_book_id(book, author)
        book_info = goodreads.get_book_info(book_id)
        if book_info is None:
            continue

        # Save the book and summons for our stats
        book = (book_id, book_info["title"], book_info["url"],
                int(time.time()))
        invocation = (str(uuid4()), book_id, comment.id, submission.id,
                      comment.body, comment.permalink, int(time.time()))
        db.save_book(book)
        db.save_invocation(invocation)

        # Build the formatted Reddit comment
        formatted_reddit_comment += format_link(book_info) + "\n\n"
        formatted_reddit_comment += format_header(cleaned, book_info) + "\n\n"
        if is_long_version(group):
            formatted_reddit_comment += format_description(book_info) + "\n\n"

    if len(formatted_reddit_comment) > 0:
        # We are responding to a comment, so let's save the post
        post = (submission.id, submission.title, submission.url)
        db.save_post(post)

        formatted_reddit_comment += "***\n\n"
        formatted_reddit_comment += make_footer()
        comment.reply(formatted_reddit_comment)
