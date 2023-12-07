import datetime

from parser_app.db_connector.connector_interface import IConnector


class STDLogger:
    def __init__(self, db_connector: IConnector):
        self.db_connector: IConnector = db_connector

    def parser_log(self, message: str, parser_name: str) -> None:
        """"""

        data = {
            'table_name': 'db_manager_parserlogs',
            'data': {
                'parser_name': parser_name,
                'log_dt': datetime.datetime.now(),
                'log_text': message
            }
        }

        self.db_connector.insert(data)
        print(message)
