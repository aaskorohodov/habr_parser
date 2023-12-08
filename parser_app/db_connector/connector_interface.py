"""Interface to build different connectors to different DBs. Intended to be used with, for example, different
SQL-dialects."""


import traceback

from abc import ABC, abstractmethod
from pathlib import Path

from parser_app.db_connector.sqlite.queries import INSERT_TEMPLATE, INSERT_OR_IGNORE_TEMPLATE, UPDATE_TEMPLATE
from parser_app.utils.annotation_support import UpdateDict, InsertIgnoreDict


class IConnector(ABC):
    """Interface to build different connectors to different DBs"""

    @abstractmethod
    def __init__(self, db_file_path: Path):
        self._db_file_path: Path = db_file_path
        self._cur = None
        self._conn = None

    @abstractmethod
    def _check_cur(self) -> None:
        """Checks if cursor exists"""

        pass

    @abstractmethod
    def _make_cur(self) -> None:
        """Creates a cursor"""

        pass

    def _check_conn(self) -> None:
        """Checks if connection is still alive. If not — makes new cursor"""

        try:
            self._cur.execute('SELECT 1')
        except:
            self._make_cur()

    @abstractmethod
    def get_hubs_to_do(self) -> dict:
        """Loads Habs, that need to be parsed

        Returns:
            Habs with their respective data"""

        pass

    @abstractmethod
    def get_articles_to_do(self) -> dict:
        """Loads articles, that need to be parsed

        Returns:
            Articles with their respective data"""

        pass

    def insert(self, data: InsertIgnoreDict) -> None:
        """Inserts provided data into desired table

        Args:
            data: dict, in format {'table_name': '', 'data': {'col_name': value}}"""

        self._check_cur()

        try:
            columns = data['data'].keys()
            values = data['data'].values()

            # Join column names and values with commas
            cols = ", ".join(columns)
            vals = ", ".join(["'{}'".format(v) for v in values])

            # Build the query string
            query = INSERT_TEMPLATE.format(data['table_name'], cols, vals)
            self._cur.execute(query)
            self._conn.commit()

        except:
            error = traceback.format_exc()
            print(error)

    def insert_or_ignore(self, data: InsertIgnoreDict) -> None:
        """Inserts data into requested table, in case data is not yet present in table

        Args:
            data: dict, in format {'table_name': '', 'data': {'col_name': value}}"""

        self._check_cur()

        try:
            columns = data['data'].keys()
            values = data['data'].values()

            # Join column names and values with commas
            cols = ", ".join(columns)
            vals = ", ".join(["'{}'".format(v) for v in values])

            # Build the query string
            query = INSERT_OR_IGNORE_TEMPLATE.format(data['table_name'], cols, vals)
            self._cur.execute(query)
            self._conn.commit()

        except:
            error = traceback.format_exc()
            print(error)

    def update(self, data: UpdateDict) -> None:
        """Updates one row

        Args:
            data: dict, in format {'table_name': '', 'where': {'col': 'val'}, 'data': {'col': 'val'}}"""

        self._check_cur()

        try:
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
            query_string = UPDATE_TEMPLATE.format(
                table=table_name,
                updates=update_string,
                conditions=condition_string)
            self._cur.execute(query_string, params)
            self._conn.commit()

        except:
            error = traceback.format_exc()
            print(error)
