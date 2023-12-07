import datetime
import os
import time

from pathlib import Path
from typing import Optional

from parser_app.db_connector.connector_factory import ConnectorFactory
from parser_app.db_connector.connector_interface import IConnector
from parser_app.logger.standard_logger import STDLogger
from parser_app.parsers.articles_parser.a_parser import ArticleParser
from parser_app.parsers.habs_parser.h_parser import HabsParser


class MainController:
    def __init__(self,
                 interval: int,
                 logger: type[STDLogger]):
        """Init"""

        self.interval = interval
        self.connector: Optional[IConnector] = None
        self.logger: type[STDLogger] | STDLogger = logger

    def start(self):
        self._get_connector()
        self._get_logger()

        while True:
            time.sleep(self.interval)
            tasks = self._check_tasks()
            habs = tasks['habs']
            articles = tasks['articles']
            if habs:
                self._parse_habs(habs)
            if articles:
                self._parse_tasks(articles)

            if not habs and not articles:
                print('Nothing to do right now, all tasks are completed.')

    def _get_connector(self) -> None:
        """"""

        db_type = os.getenv('DB_TYPE')
        db_file_path = os.getenv('DB_FILE_PATH')

        connector = ConnectorFactory.get_parser(db_type)
        if isinstance(connector, Exception):
            raise connector
        else:
            self.connector = connector(Path(db_file_path))

    def _get_logger(self) -> None:
        """"""

        self.logger = self.logger(self.connector)

    def _check_tasks(self):
        """"""

        tasks = {
            'habs': {},
            'articles': {}
        }

        habs = self.connector.get_hubs_to_do()
        tasks['articles'] = self.connector.get_articles_to_do()

        habs_to_parse = self._check_habs(habs)
        tasks['habs'] = habs_to_parse

        return tasks

    def _check_habs(self, habs: dict) -> dict:
        """"""

        parse_this = {}

        current_dt = datetime.datetime.now()
        for hab_name, data in habs.items():
            last_parsed = data['last_parsed']
            parse_interval_minutes = data['parse_interval_minutes']

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

    def _parse_habs(self, habs: dict) -> None:
        """"""

        h_parser = HabsParser(habs, self.logger, self.connector)
        h_parser.parse()

    def _parse_tasks(self, articles: dict) -> None:
        """"""

        a_parser = ArticleParser(articles, self.logger, self.connector)
        a_parser.parse()
