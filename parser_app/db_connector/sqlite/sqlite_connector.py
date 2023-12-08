"""Connector for SQLite dialect DB"""


import sqlite3

from pathlib import Path

from parser_app.db_connector.connector_interface import IConnector
from parser_app.db_connector.sqlite.queries import GET_ARTICLE_TO_DO, GET_HUB_TO_DO


class SQLiteFromFileConnector(IConnector):
    """Connector for SQLite dialect DB

    Attributes:
        db_file_path: Path to DB (file)
        _conn: Connection-object
        _cur: Cursor"""

    def __init__(self, db_file_path: Path):
        """Init

        Args:
            db_file_path: Path to file with DB"""

        self.db_file_path = db_file_path
        self._conn = None
        self._cur = None

    def _check_cur(self) -> None:
        """Checks connection and returns cursor"""

        try:
            if not self._cur:
                self._make_cur()
            self._check_conn()
        except Exception as e:
            print(e)

    def _make_cur(self) -> None:
        """Makes new cursor and saves it to self._cur"""

        if self._conn is None:
            self._conn = sqlite3.connect(self.db_file_path)
        self._cur = self._conn.cursor()

    # PUBLIC

    def get_hubs_to_do(self) -> dict:
        self._check_cur()
        self._cur.execute(GET_HUB_TO_DO)
        rows = self._cur.fetchall()
        results = {}
        for row in rows:
            results[row[0]] = {
                'url': row[1],
                'last_parsed': row[2],
                'parse_interval_minutes': row[3],
                'hab_id': row[4],
            }

        return results

    def get_articles_to_do(self) -> dict:
        self._check_cur()
        self._cur.execute(GET_ARTICLE_TO_DO)
        rows = self._cur.fetchall()
        results = {}
        for row in rows:
            results[row[0]] = {
                'habr_id': row[1],
                'url': row[2],
                'header': row[0]
            }

        return results
