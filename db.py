from sqlite_wrapper import SQLite


class DB:
    def __init__(self):
        self.sqlite = SQLite.get()
        self.conn = self.sqlite.conn

    def check_connection(self):
        if self.conn is None:
            raise Exception("Bad sqlite connection")

    def create_tables(self):
        sql_create_books_table = '''
            CREATE TABLE IF NOT EXISTS books
            (
                id              INT PRIMARY KEY NOT NULL,
                title           TEXT NOT NULL,
                url             TEXT NOT NULL,
                times_requested INT DEFAULT 1,
                updated         INT NOT NULL
            );
        '''

        sql_create_summons_table = '''
            CREATE TABLE IF NOT EXISTS invocations
            (
                id          TEXT PRIMARY KEY,
                book_id     INT NOT NULL,
                comment_id  TEXT NOT NULL,
                post_id     TEXT NOT NULL,
                body        TEXT NOT NULL,
                permalink   TEXT NOT NULL,
                created     INT NOT NULL,
                FOREIGN     KEY (book_id) REFERENCES books (id)
                FOREIGN     KEY (post_id) REFERENCES posts (id)
            );
        '''

        sql_create_posts_table = '''
            CREATE TABLE IF NOT EXISTS posts
            (
                id      TEXT PRIMARY KEY NOT NULL,
                title   TEXT NOT NULL,
                url     TEXT NOT NULL
            );
        '''

        sql_create_cache_table = '''
            CREATE TABLE IF NOT EXISTS cache
            (
                book_id         INT PRIMARY KEY NOT NULL,
                url             TEXT NOT NULL,
                pub_year        INT NOT NULL,
                shelves         TEXT NOT NULL,
                authors         TEXT NOT NULL,
                title           TEXT NOT NULL,
                description     TEXT NOT NULL,
                updated_at      INT NOT NULL,
                FOREIGN         KEY (book_id) REFERENCES books (id)
            );
        '''

        self.conn.execute(sql_create_books_table)
        self.conn.execute(sql_create_summons_table)
        self.conn.execute(sql_create_posts_table)
        self.conn.execute(sql_create_cache_table)

        print("DB: Tables created successfully")

    def count_invocations(self):
        select = '''
            SELECT COUNT(*) FROM invocations
        '''

        self.check_connection()
        cursor = self.conn.execute(select)
        count = cursor.fetchall()
        return count[0][0]

    def count_comment_invocations(self, comment_id):
        select = '''
            SELECT COUNT(*) FROM invocations
            WHERE comment_id = ?
        '''

        self.check_connection()
        cursor = self.conn.execute(select, (comment_id, ))
        count = cursor.fetchall()
        return count[0][0]

    def count_book_requests(self, book_id):
        select = '''
            SELECT times_requested FROM books
            WHERE id = ?
        '''

        self.check_connection()
        cursor = self.conn.execute(select, (book_id, ))
        count = cursor.fetchall()
        return count[0][0]

    def save_book(self, book):
        insertion = '''
            INSERT INTO books(id, title, url, updated)
            VALUES(?,?,?,?)
            ON CONFLICT(id) DO UPDATE
            SET times_requested = times_requested + 1
        '''

        self.check_connection()
        self.conn.execute(insertion, book)
        self.conn.commit()

    def save_post(self, post):
        insertion = '''
            INSERT OR IGNORE INTO posts(id, title, url)
            VALUES(?,?,?)
        '''

        self.check_connection()
        self.conn.execute(insertion, post)
        self.conn.commit()

    def save_invocation(self, invocation):
        insertion = '''
            INSERT INTO invocations(id, book_id, comment_id, post_id, body, permalink, created)
            VALUES(?,?,?,?,?,?,?)
        '''

        self.check_connection()
        self.conn.execute(insertion, invocation)
        self.conn.commit()

    def update_cache(self, cache_entry):
        insertion = '''
            INSERT INTO cache(
                book_id,
                url,
                pub_year,
                permalink,
                authors,
                title,
                description,
                updated_at
            )
            VALUES(?,?,?,?,?,?,?,?)
        '''

        self.check_connection()
        self.conn.execute(insertion, cache_entry)
        self.conn.commit()
