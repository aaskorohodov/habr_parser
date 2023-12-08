"""Parser for Habs"""


import asyncio
import datetime
import os

from bs4 import BeautifulSoup

from parser_app.db_connector.connector_interface import IConnector
from parser_app.logger.standard_logger import STDLogger
from parser_app.parsers.pasrser_interface import ParserInterface


class HabsParser(ParserInterface):
    """Parser for Habrs

    Attributes:
        connector: Connector to get data from/in DB
        parser_name: Name of this concrete parser
        habs: Dict with habs, loaded from DB, to parse them
        logger: Logger-object, to log this parser's progress
        parallel_jobs: Number of jobs to be executed in parallel"""

    def __init__(self,
                 habs: dict,
                 logger: STDLogger,
                 connector: IConnector):
        """Init

        Args:
            habs: Dict with habs, loaded from DB, to parse them
            logger: Logger-object, to log this parser's progress
            connector: Connector to get data from/in DB"""

        self.connector: IConnector = connector
        self.parser_name: str = 'Habs parser'
        self.habs: dict = habs
        self.logger: STDLogger = logger
        self.parallel_jobs = 5

    def parse(self) -> None:
        """Hit to start parsing"""

        asyncio.run(self.parse_pages(self.habs))

    def parse_data_from_html(self, completed_jobs: list) -> None:
        """Parses data from loaded HTML

        Args:
            completed_jobs: List with dicts, where each dict stores data, related to some web-page"""

        for job in completed_jobs:
            html = job.get('html')
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                article_headers = soup.find_all('h2', class_='tm-title tm-title_h2')

                for header in article_headers:
                    link = header.find('a')
                    if link:
                        article_header = link.find('span').text
                        article_url = link.get('href')
                        if article_header and article_url:
                            article_url = f'https://habr.com{article_url}'
                            print('')
                            print(article_header)
                            print(article_url)
                            job['article_header'] = article_header
                            job['article_url'] = article_url
                            self._save_articles(job)

                self._update_hab(job)

    def _save_articles(self, data: dict) -> None:
        """Saves data, collected for articles (and articles themselves)

        Args:
            data: Data, related to a specific article"""

        article_table: str = os.getenv('ARTICLES_TABLE')
        data = {
            'table_name': article_table,
            'data': {
                'url': data['article_url'],
                'date_collected': datetime.datetime.now(),
                'parse_this': 1,
                'header': data['article_header'],
                'habr_id': data['hab_id']
            }
        }

        self.connector.insert_or_ignore(data)

    def _update_hab(self, data: dict) -> None:
        """Updates Habr's data in DB, after habr is parsed

        Args:
            data: Data, related tio this Habr"""

        table_name: str = os.getenv('HABS_TABLE')
        data = {
            'table_name': table_name,
            'where': {
                'id': data['hab_id']
            },
            'data': {
                'last_parsed': datetime.datetime.now(),
                'last_status': 'Success!'
            }
        }

        self.connector.update(data)
