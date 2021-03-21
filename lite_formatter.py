from formatter import Formatter

class LiteFormatter(Formatter):
    def format_link(self):
        title = self.book_info["title"]
        url = self.book_info["url"]

        return "[**%s**](%s)" % (title, url)

    def format_header(self):
        year = self.book_info["pub_year"]
        authors = ", ".join(self.book_info["authors"])
        s = "s" if self.book_suggestions > 1 else ""

        return "^(By: %s | Published: %s | Suggested %s time%s)" % (
            authors, year or "?", self.book_suggestions, s)

    def format_book_footer(self):
        return ""
    
    def supports_long_version(self):
        return False