from __future__ import annotations
from typing import TYPE_CHECKING

from parser_app.db_connector.sqlite.sqlite_connector import SQLiteConnector


if TYPE_CHECKING:
    from parser_app.db_connector.connector_interface import IConnector


class ConnectorFactory:
    __connectors = {
            'sqlite': SQLiteConnector,
        }

    @staticmethod
    def get_parser(db_type: str) -> type[IConnector] | LookupError:
        """"""

        selected_connector = ConnectorFactory.__connectors.get(db_type, None)
        if not selected_connector:
            selected_connector = LookupError(f'Connector for DB "{db_type}" does not exist!')

        return selected_connector
