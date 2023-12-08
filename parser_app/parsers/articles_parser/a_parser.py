"""Parser for Articles"""


import asyncio
import datetime
import os

from bs4 import BeautifulSoup, NavigableString
from colorama import Fore, Style

from parser_app.db_connector.connector_interface import IConnector
from parser_app.logger.standard_logger import STDLogger
from parser_app.parsers.pasrser_interface import ParserInterface


class ArticleParser(ParserInterface):
    """Parser for Articles

    Attributes:
        connector: Connector to get data from/in DB
        parser_name: Name of this concrete parser
        articles: Dict with articles, loaded from DB, to parse them
        logger: Logger-object, to log this parser's progress
        parallel_jobs: Number of jobs to be executed in parallel"""

    def __init__(self,
                 articles: dict,
                 logger: STDLogger,
                 connector: IConnector):
        """Init

        Args:
            articles: Dict with articles, loaded from DB, to parse them
            logger: Logger-object, to log this parser's progress
            connector: Connector to get data from/in DB"""

        self.connector: IConnector = connector
        self.parser_name: str = 'Habs parser'
        self.articles: dict = articles
        self.logger: STDLogger = logger
        self.parallel_jobs = 5

    def parse(self) -> None:
        """Hit to start parsing"""

        asyncio.run(self.parse_pages(self.articles))

    def parse_data_from_html(self, completed_jobs: list) -> None:
        """Parses data from loaded HTML

        Args:
            completed_jobs: List with dicts, where each dict stores data, related to some web-page"""

        for job in completed_jobs:
            html = job.get('html')
            if html:
                # Getting data from HTML
                soup = BeautifulSoup(html, 'html.parser')
                publication_dt = self._get_publication_dt(soup)
                author_link, author_name = self._get_author_data(soup)
                article_text = self._get_article_text(soup)

                # Printing collected data in a nice way
                print('––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––')
                self._print_collected_data('Article url:', job.get("url"))
                self._print_collected_data('Article header:', job.get("header"))
                self._print_collected_data('Article date:', publication_dt)
                self._print_collected_data('Author name:', author_name)
                self._print_collected_data('Author link:', author_link)
                self._print_collected_data('Author text:', article_text)
                print('')

                # Updating collection, related tio this web-page and sending it into DB
                job['publication_dt'] = publication_dt
                job['author_link'] = author_link
                job['author_name'] = author_name
                job['article_text'] = article_text
                self._update_article(job)

    def _get_publication_dt(self, soup: BeautifulSoup) -> datetime.datetime | None:
        """Tries to get DT of an article from HTML-page (from soup, technically)

        Args:
            soup: Soup object (BS) with loaded HTML-page
        Returns:
            DT-object or None, in case DT was not retrieved"""

        try:
            time_tag = soup.find('span', class_='tm-article-datetime-published').find('time')
            date_string = time_tag.get('datetime')
            parsed_datetime = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            parsed_datetime = None

        return parsed_datetime

    def _get_author_data(self, soup: BeautifulSoup) -> tuple[str, str] | tuple[None, None]:
        """Tries to get Author's name and link and from HTML-page (from soup, technically)

        Args:
            soup: Soup object (BS) with loaded HTML-page
        Returns:
            tuple(author_link, author_name) or tuple with Nones, in case of a failure"""

        try:
            a_tag = soup.find('a', class_='tm-user-info__username')
            author_link = a_tag.get('href')
            author_link = f'https://habr.com{author_link}'
            author_name = a_tag.text.strip()
            return author_link, author_name
        except:
            return None, None

    def _get_article_text(self, soup: BeautifulSoup) -> str:
        """Tries to get articles text from HTML-page (from soup, technically)

        Args:
            soup: Soup object (BS) with loaded HTML-page
        Returns:
            Article's text, including headers"""

        try:
            article_text_list = []

            # <div> with articles text and some other stuff
            content_div = soup.find('div', xmlns='http://www.w3.org/1999/xhtml')

            # Simple way - trying to get text, that was arranged properly
            for tag in content_div.find_all(['p', 'h2']):
                article_text_list.append(tag.get_text(separator=' ', strip=True))

            # Sometimes text is scattered with no tags – collecting what there is
            for child in content_div.children:
                if isinstance(child,
                              NavigableString) and child.strip():
                    article_text_list.append(child.strip())

            # Joining collected text with linebreaks, representing <h2> or <p>
            all_text = '\n'.join(article_text_list)
        except:
            all_text = ''

        return all_text

    def _print_collected_data(self,
                              title: str,
                              msg: any,
                              title_length: int = 20,
                              msg_length: int = 150) -> None:
        """Print collected data in a nice way

        Args:
            title: Any title, to represent what is going to be print
            msg: Main text, that needs to be print
            title_length: Max length, allowed for a title (title will be shortened to this length)
            msg_length: Max length, allowed for a main message (main message will be shortened to this length)"""

        # Cutting msg and title to a max length, specified in args
        try:
            title = str(title)
            msg = str(msg)
            if len(title) > title_length:
                title = str(title)[:title_length] + '...'
            if len(msg) > msg_length:
                msg = str(msg)[:msg_length] + '...'
        except:
            pass

        print(Fore.GREEN + title + Style.RESET_ALL)
        print(Fore.LIGHTCYAN_EX + f'\t{msg}' + Style.RESET_ALL)

    def _update_article(self, data: dict) -> None:
        """Collects data for an SQL-query and triggers it

        Args:
            data: Data, related to some article"""

        table_name: str = os.getenv('ARTICLES_TABLE')
        data = {
            'table_name': table_name,
            'where': {
                'header': data['header']
            },
            'data': {
                'date_parsed': datetime.datetime.now(),
                'last_status': 'Success!',
                'parse_this': 0,
                'article_text': data['article_text'],
                'article_date': data['publication_dt'],
                'author_name': data['author_name'],
                'author_url': data['author_link']
            }
        }

        self.connector.update(data)
