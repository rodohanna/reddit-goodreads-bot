from formatter import Formatter
import re

class DefaultFormatter(Formatter):
    def format_link(self):
        title = self.book_info["title"]
        url = self.book_info["url"]

        return "[**%s**](%s)" % (title, url)

    def format_header(self):
        pages = self.book_info["num_pages"]
        year = self.book_info["pub_year"]
        shelves = ", ".join(self.book_info["shelves"])
        authors = ", ".join(self.book_info["authors"])

        return "^(By: %s | %s pages | Published: %s | Popular Shelves: %s)" % (
            authors, pages or "?", year or "?", shelves)

    def format_description(self):
        description = self.book_info["description"]
        if description is None:
            return ""
        description = re.sub('<.*?>', '', description.replace("<br />", "\n"))

        chunks = [">" + chunk for chunk in description.split("\n")]

        return "\n".join(chunks)

    def format_book_footer(self):
        s = "s" if self.book_suggestions > 1 else ""
        return "^(This book has been suggested %s time%s)" % (self.book_suggestions, s)
