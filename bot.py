import praw
import re
import time
from goodreads import GoodReads

reddit = praw.Reddit()
goodreads = GoodReads()
cleanr = re.compile('<.*?>')
search_link = "https://www.goodreads.com/search?q=%s&search_type=books&search[field]=title"

for comment in reddit.subreddit("test").stream.comments(skip_existing=True):
    matches = re.findall("\{([^}]+)\}", comment.body)
    print("comment: ", comment.body)
    print("matches: ", matches)
    formatted_reddit_comment = ""
    for match in matches:
        book, *author = match.rsplit("by", 1)
        book = book.strip()
        author = author[0].strip() if author else None
        print("book: ", book)
        print("author: ", author)

        book_info = goodreads.get_book_info(book, author)

        if book_info is None:
            formatted_reddit_comment += "[Click on this link to search GoodReads for \"%s\"](%s)\n" % (
                book, search_link % book)
            continue

        print("requested title: ", book)
        print("returned title: ", book_info["title"])

        book_info["description"] = re.sub(
            cleanr, '', book_info["description"].replace("<br />", "\n"))

        formatted_reddit_comment += "[%s](%s)\n\n" % (book_info["title"],
                                                      book_info["url"])

        chunks = [
            ">" + chunk for chunk in book_info["description"].split("\n")
        ]

        formatted_reddit_comment += "\n".join(chunks)

        formatted_reddit_comment += "\n\n^(I'm a bot so it's possible I got the book wrong. Click on this link to search GoodReads for) [%s](%s)\n" % (
            book, search_link % book)

        formatted_reddit_comment += "\n\n"

    print(formatted_reddit_comment)
    if len(formatted_reddit_comment) > 0:
        comment.reply(formatted_reddit_comment)
