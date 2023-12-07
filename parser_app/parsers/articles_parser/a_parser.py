import asyncio
import datetime
import os

from bs4 import BeautifulSoup, NavigableString

from parser_app.db_connector.connector_interface import IConnector
from parser_app.logger.standard_logger import STDLogger
from parser_app.parsers.pasrser_interface import ParserInterface


class ArticleParser(ParserInterface):
    def __init__(self, articles: dict, logger: STDLogger, connector: IConnector):
        self.connector: IConnector = connector
        self.parser_name: str = 'Habs parser'
        self.articles: dict = articles
        self.logger: STDLogger = logger

    def parse(self) -> None:
        """"""

        asyncio.run(self.parse_pages(self.articles))

    def parse_data_from_html(self, completed_jobs):
        """"""

        for job in completed_jobs:
            html = job.get('html')
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                publication_dt = self._get_publication_dt(soup)
                author_link, author_name = self._get_author_data(soup)
                article_text = self._get_article_text(soup)

                print('')
                print(publication_dt)
                print(author_link)
                print(author_name)
                print(article_text)

                job['publication_dt'] = publication_dt
                job['author_link'] = author_link
                job['author_name'] = author_name
                job['article_text'] = article_text

                self._update_article(job)

    def _get_publication_dt(self, soup: BeautifulSoup) -> datetime.datetime | None:
        """"""

        time_tag = soup.find('span', class_='tm-article-datetime-published').find('time')
        date_string = time_tag.get('datetime')
        try:
            parsed_datetime = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            parsed_datetime = None

        return parsed_datetime

    def _get_author_data(self, soup: BeautifulSoup) -> tuple[str, str] | None:
        """"""

        try:
            a_tag = soup.find('a', class_='tm-user-info__username')
            author_link = a_tag.get('href')
            author_link = f'https://habr.com{author_link}'
            author_name = a_tag.text.strip()
            return author_link, author_name
        except:
            return None

    def _get_article_text(self, soup: BeautifulSoup) -> str | None:
        """"""

        try:
            article_text_list = []

            content_div = soup.find('div', xmlns='http://www.w3.org/1999/xhtml')

            for tag in content_div.find_all(['p', 'h2']):
                article_text_list.append(tag.get_text(separator=' ', strip=True))

            for child in content_div.children:
                if isinstance(child,
                              NavigableString) and child.strip():
                    article_text_list.append(child.strip())

            all_text = '\n'.join(article_text_list)

            # content_div = soup.find('div', id='post-content-body')
            # for tag in content_div.find_all(['p', 'h2']):
            #     article_text_list.append(tag.get_text(separator=' ', strip=True))
            #
            # divs_with_namespace = soup.find_all('div', {'xmlns': 'http://www.w3.org/1999/xhtml'})
            # for div in divs_with_namespace:
            #     article_text_list.append(div.get_text(separator=' ', strip=True))

            # all_text = '\n'.join(article_text_list)
        except:
            all_text = None

        return all_text

    def _update_article(self, data: dict) -> None:
        """"""

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
