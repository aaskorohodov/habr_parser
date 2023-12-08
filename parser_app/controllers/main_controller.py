"""Main application controller"""


import datetime
import os
import time

from pathlib import Path
from typing import Optional

from parser_app.db_connector.connector_factory import ConnectorFactory
from parser_app.db_connector.connector_interface import IConnector
from parser_app.logger.standard_logger import STDLogger
from parser_app.parsers.parser_factory import ParserFactory


class MainController:
    """Main application controller

    Attributes:
        interval: Interval in seconds, in which DB will be checked for updates
        connector: Connector to DB
        logger: Logger, to log anything into DB"""

    def __init__(self,
                 interval: int,
                 logger: type[STDLogger]):
        """Init

        Args:
            interval: Interval in seconds, in which DB will be checked for updates
            logger: Logger, to log anything into DB"""

        self.interval = interval
        self.connector: Optional[IConnector] = None
        self.logger: type[STDLogger] | STDLogger = logger

    def start(self):
        """Starts an endless cycle"""

        self._get_connector()
        self._activate_logger()

        while True:
            # Waiting a bit, not to overload DB with queries
            time.sleep(self.interval)

            # Getting Habrs and Articles, that need to be parsed (or empty collection, if all done)
            tasks = self._check_tasks()
            habrs = tasks['habrs']
            articles = tasks['articles']

            if habrs:
                self._parse_this(habrs, 'habrs')
            if articles:
                self._parse_this(articles, 'articles')

            if not habrs and not articles:
                print('👍 Nothing to do right now, all tasks are completed! 👍')
                print('–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')

    def _get_connector(self) -> None:
        """Gets connector, specified in for for DB, set in .env"""

        db_type = os.getenv('DB_TYPE')
        db_file_path = os.getenv('DB_FILE_PATH')

        connector = ConnectorFactory.get_parser(db_type)
        if isinstance(connector, Exception):
            raise connector
        else:
            self.connector = connector(Path(db_file_path))

    def _activate_logger(self) -> None:
        """Activates provided Logger"""

        self.logger = self.logger(self.connector)

    def _check_tasks(self) -> dict:
        """Reads DB and checks, which Habrs and Articles can be parsed

        Returns:
            Dict with Habrs and Articles, if there is any to do right now"""

        tasks = {
            'habrs': {},
            'articles': {}
        }

        habs = self.connector.get_hubs_to_do()
        tasks['articles'] = self.connector.get_articles_to_do()

        habs_to_parse = self._check_habs(habs)
        tasks['habrs'] = habs_to_parse

        return tasks

    def _check_habs(self, habrs: dict) -> dict:
        """Checks, which Habrs can be executed now (each Habrs have a specific time-window)

        Args:
            habrs: Habrs from DB
        Returns:
            Only those Habrs, that can be executed now"""

        # This will be Habrs, which can be parsed now (due to their timing, specified in DB)
        parse_this = {}

        current_dt = datetime.datetime.now()
        for hab_name, data in habrs.items():
            last_parsed = data['last_parsed']
            parse_interval_minutes = data['parse_interval_minutes']

            # In case this Habr have never being parsed before (new Habr)
            if not last_parsed:
                parse_this[hab_name] = data
            else:
                delta = datetime.timedelta(minutes=parse_interval_minutes)
                last_parsed_dt = datetime.datetime.strptime(last_parsed, '%Y-%m-%d %H:%M:%S.%f')
                next_parsing_dt = last_parsed_dt + delta
                if current_dt >= next_parsing_dt:
                    parse_this[hab_name] = data
                else:
                    msg = f'Hab "{hab_name}" is completed, next schedule is {next_parsing_dt}'
                    print(msg)

        return parse_this

    def _parse_this(self, parsing_tasks: dict, parsing_type: str) -> None:
        """Selects a parser and activates it

        Args:
            parsing_tasks: Collection with Habrs or Articles to parse
            parsing_type: String, that indicates which parser should be used"""

        parser = ParserFactory.get_parser(parsing_type)
        if isinstance(parser, Exception):
            raise Exception
        else:
            parser = parser(parsing_tasks, self.logger, self.connector)
            parser.parse()
