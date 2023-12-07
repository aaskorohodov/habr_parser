import traceback

from abc import ABC, abstractmethod
from pathlib import Path

from parser_app.utils.annotation_support import UpdateDict


class IConnector(ABC):
    @abstractmethod
    def __init__(self, db_file_path: Path):
        self.db_file_path = db_file_path
        self._cur = None
        self._conn = None

    @abstractmethod
    def _check_cur(self):
        pass

    @abstractmethod
    def _make_cur(self):
        pass

    def _check_conn(self) -> None:
        """Checks if connection is still alive. If not — makes new cursor"""

        try:
            self._cur.execute('SELECT 1')
        except:
            self._make_cur()

    @abstractmethod
    def get_hubs_to_do(self) -> dict:
        pass

    @abstractmethod
    def get_articles_to_do(self) -> dict:
        pass

    def insert(self, data: dict) -> None:
        """Inserts provided data into desired table

        Args:
            data: dict, in form {'table_name': '', 'data': {'col_name': value}}
        Raises:
            ConnectionError: In case data was not inserted"""

        self._check_cur()

        try:
            columns = data['data'].keys()
            values = data['data'].values()

            # Join column names and values with commas
            cols = ", ".join(columns)
            vals = ", ".join(["'{}'".format(v) for v in values])

            # Build the query string
            query = "INSERT INTO {}({}) VALUES ({})".format(data['table_name'], cols, vals)
            self._cur.execute(query)
            self._conn.commit()

        except:
            error = traceback.format_exc()

            raise ConnectionError(error)

    def insert_or_ignore(self, data: dict) -> None:
        """"""

        self._check_cur()

        try:
            columns = data['data'].keys()
            values = data['data'].values()

            # Join column names and values with commas
            cols = ", ".join(columns)
            vals = ", ".join(["'{}'".format(v) for v in values])

            # Build the query string
            query = "INSERT OR IGNORE INTO {}({}) VALUES ({})".format(data['table_name'], cols, vals)
            self._cur.execute(query)
            self._conn.commit()

        except:
            error = traceback.format_exc()

            raise ConnectionError(error)

    def update(self, data: UpdateDict) -> None:
        """Updates one row

        Args:
            data: dict, in form {'table_name': '', 'where': {'col': 'val'}, 'data': {'col': 'val'}}
        Raises:
            ConnectionError: In case data was not inserted"""

        self._check_cur()

        try:
            query = "UPDATE {table} SET {updates} WHERE {conditions};"

            table_name = data['table_name']
            where_clause = data['where']
            data_dict = data['data']

            # Create the list of updates
            update_list = [f"{col}=?" for col in data_dict.keys()]
            update_string = ", ".join(update_list)
            params = tuple(data_dict.values())

            # Create the list of conditions
            condition_list = [f"{col}='{val}'" for col, val in where_clause.items()]
            condition_string = " AND ".join(condition_list)

            # Build the final query string
            query_string = query.format(table=table_name, updates=update_string, conditions=condition_string)
            self._cur.execute(query_string, params)
            self._conn.commit()

        except:
            error = traceback.format_exc()
            print(error)
