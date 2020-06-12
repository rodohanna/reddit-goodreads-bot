import praw
import re
import time
from goodreads import GoodReads

reddit = praw.Reddit()
goodreads = GoodReads()
cleanr = re.compile('<.*?>')
search_link = "https://www.goodreads.com/search?q=%s&search_type=books&search[field]=title"


def get_book_and_author(match):
    book, *author = match.rsplit("by", 1)
    book = book.strip()
    author = author[0].strip() if author else None

    return (book, author)


def format_link(book_info):
    title = book_info["title"]
    url = book_info["url"]

    return "[**%s**](%s)" % (title, url)


def format_description(book_info):
    description = book_info["description"]

    description = re.sub(cleanr, '', description.replace("<br />", "\n"))

    chunks = [">" + chunk for chunk in description.split("\n")]

    return "\n".join(chunks)


def format_disclaimer(book):
    return "^(I'm a bot so it's possible I got the book wrong. Click on this link to search GoodReads for) [%s](%s)\n" % (
        book, search_link % book)


def format_header(book, book_info):
    pages = book_info["num_pages"]
    year = book_info["pub_year"]
    shelves = ", ".join(book_info["shelves"])
    authors = ", ".join(book_info["authors"])

    return "^(By: %s | %s pages | Published: %s | Popular Shelves: %s | )[^(Search \"%s\")](%s)" % (
        authors, pages, year, shelves, book, search_link % book)


def is_long_version(group):
    return group.count("{") == 2


def is_short_version(group):
    return group.count("{") == 1


def clean_group(group):
    return group.replace("{", "").replace("}", "")


for comment in reddit.subreddit("test").stream.comments(skip_existing=True):
    print("comment: ", comment.body)
    formatted_reddit_comment = ""
    for m in re.finditer('\{\{([^}]+)\}\}|\{([^}]+)\}', comment.body):
        group = m.group()
        cleaned = clean_group(group)

        print("group: ", group)
        print("cleaned: ", cleaned)

        book, author = get_book_and_author(cleaned)

        book_info = goodreads.get_book_info(book, author)

        if book_info is None:
            continue

        formatted_reddit_comment += format_link(book_info) + "\n\n"

        formatted_reddit_comment += format_header(book, book_info) + "\n\n"

        if is_long_version(group):
            formatted_reddit_comment += format_description(book_info) + "\n\n"

    if len(formatted_reddit_comment) > 0:
        formatted_reddit_comment += "***\n\n"
        comment.reply(formatted_reddit_comment)
