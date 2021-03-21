from formatter import Formatter

class LiteFormatter(Formatter):
    def format_link(self):
        title = self.book_info["title"]
        url = self.book_info["url"]

        return "[**%s**](%s)" % (title, url)

    def format_header(self):
        year = self.book_info["pub_year"]
        authors = ", ".join(self.book_info["authors"])

        return self.get_section_separator() + "^(By: %s | Published: %s)" % (
            authors, year or "?")

    def format_book_footer(self):
        return ""
    
    def supports_long_version(self):
        return False
    
    def get_section_separator(self):
        return '\n'