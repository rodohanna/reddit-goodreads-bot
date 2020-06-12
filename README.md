# u/goodreads-bot

A Reddit bot that comments GoodReads' data when summoned.

Example:

If someone makes a comment like:

`I think you would like {The Hobbit}`

The bot will add a comment with a GoodReads link, author, number of pages, year published, popular shelves (up to 5), and a link to a prepopulated search for "The Hobbit".

If someone makes a comment like:

`Maybe you should check out {{Dark Matter}}`

The bot will add a comment with all of the information listed above AND the GoodReads' description.

## Installation

Requirements:

- [Python 3](https://www.python.org/download/releases/3.0/)
- [Pip](https://pip.pypa.io/en/stable/)

Install dependencies and start the bot

```bash
pip install -r requirements.txt
python driver.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
