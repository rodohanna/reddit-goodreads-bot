import praw
import re
import time
from goodreads import GoodReads

reddit = praw.Reddit()
goodreads = GoodReads()
cleanr = re.compile('<.*?>')

for comment in reddit.subreddit("test").stream.comments(skip_existing=True):
    matches = re.findall("\{([^}]+)\}", comment.body)
    print("comment: ", comment.body)
    print("matches: ", matches)
    for match in matches:
        book, *author = match.rsplit("by", 1)
        book = book.strip()
        author = author[0].strip() if author else None
        print("book: ", book)
        print("author: ", author)

        book_info = goodreads.get_book_info(book, author)
        book_info["description"] = re.sub(
            cleanr, '', book_info["description"].replace("<br />", "\n"))
        print("book info: ", book_info)
