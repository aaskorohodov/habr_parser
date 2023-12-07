import sqlite3

from pathlib import Path

from parser_app.db_connector.connector_interface import IConnector


class SQLiteConnector(IConnector):
    def __init__(self, db_file_path: Path):
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
        """"""

        self._check_cur()

        query = 'SELECT name, url, last_parsed, parse_interval_minutes, id ' \
                'FROM db_manager_habrs ' \
                'WHERE is_active = true'

        self._cur.execute(query)
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
        """"""

        self._check_cur()

        query = 'SELECT header, habr_id, url ' \
                'FROM db_manager_articles ' \
                'WHERE parse_this = 1'

        self._cur.execute(query)
        rows = self._cur.fetchall()
        results = {}
        for row in rows:
            results[row[0]] = {
                'habr_id': row[1],
                'url': row[2],
                'header': row[0]
            }

        return results
