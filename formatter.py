class Formatter:
    def __init__(self, book_info, cleaned, book_suggestions):
        self.book_info = book_info
        self.cleaned = cleaned
        self.book_suggestions = book_suggestions
    
    def format_link(self):
        pass

    def format_header(self):
        pass

    def format_description(self):
        pass

    def format_book_footer(self):
        pass

    def supports_long_version(self):
        return True