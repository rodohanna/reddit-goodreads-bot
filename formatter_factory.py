from default_formatter import DefaultFormatter
from lite_formatter import LiteFormatter

class FormatterFactory:
    @staticmethod
    def for_subreddit(subreddit_name, book_info, cleaned, book_suggestions):
        print("building formatter for: " + subreddit_name)
        if subreddit_name.lower() == "romancebooks":
            return DefaultFormatter(
                    book_info=book_info,
                    cleaned=cleaned,
                    book_suggestions=book_suggestions)
        elif subreddit_name.lower() == "test":
            return LiteFormatter(
                book_info=book_info,
                cleaned=cleaned,
                book_suggestions=book_suggestions)
        else:
            return DefaultFormatter(
                    book_info=book_info,
                    cleaned=cleaned,
                    book_suggestions=book_suggestions)