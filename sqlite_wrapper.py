import sqlite3
from configparser import ConfigParser

config = ConfigParser()
config.read('praw.ini')
config = config["DEFAULT"]


class SQLite:
    __instance = None
    sqlite_db = config["sqlite_db"]

    @staticmethod
    def get():
        if SQLite.__instance == None:
            SQLite()
        return SQLite.__instance

    def __init__(self):
        if SQLite.__instance != None:
            raise Exception("Singleton error")
        else:
            SQLite.__instance = self
            self.conn = sqlite3.connect(self.sqlite_db)
