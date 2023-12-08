"""Standard logger"""


import datetime
import os

from parser_app.db_connector.connector_interface import IConnector


class STDLogger:
    """Standard Logger, designed to log data into DB and print it

    Attributes:
        db_connector: Connector, that logger will use to save massages into DB"""

    def __init__(self, db_connector: IConnector):
        """Init

        Args:
            db_connector: Connector, that logger will use to save massages into DB"""

        self.db_connector: IConnector = db_connector

    def parser_log(self, message: str, parser_name: str = 'Undefined') -> None:
        """Logs data from Parsers into DN and prints it

        Args:
            message: Message to be logged
            parser_name: Name of the parser, which logged this message"""

        table_name: str = os.getenv('LOGS_TABLE')
        data = {
            'table_name': table_name,
            'data': {
                'parser_name': parser_name,
                'log_dt': datetime.datetime.now(),
                'log_text': message
            }
        }

        self.db_connector.insert(data)
        print(f'{parser_name}: {message}')
