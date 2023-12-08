"""Interface/Base-class (Python-style anarchy) to create different parsers"""


import asyncio
import aiohttp

from abc import ABC, abstractmethod
from typing import Awaitable


class ParserInterface(ABC):
    """Interface to create different parsers

    Attributes:
        logger: Logger-object to log messages into DB (or/and printing)
        parser_name: Name of the concrete implementation
        parallel_jobs: Number of web-pages, that will be parsed in parallel"""

    @abstractmethod
    def __init__(self):
        """Init"""

        self.logger = None
        self.parser_name = ''
        self.parallel_jobs = 5

    @abstractmethod
    def parse_data_from_html(self, completed_jobs: list) -> None:
        """Concrete logic to parse data from loaded HTML

        Args:
            completed_jobs: Each job is a collection, related to a single loaded page"""

        pass

    async def fetch_page(self,
                         session: aiohttp.client.ClientSession,
                         job_data: dict) -> dict:
        """Fetches a web-page

        Args:
            session: AIOHttp's session object
            job_data: Data, related to concrete web-page"""

        url = job_data['url']
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                msg = f'URL {url} was successfully fetched!'
                self.logger.parser_log(msg, parser_name=self.parser_name)
                job_data['html'] = html

                return job_data
            else:
                msg = f'Failed to fetch url {url}'
                self.logger.parser_log(msg, parser_name=self.parser_name)
                job_data['html'] = None

                return job_data

    async def process_url(self,
                          semaphore: asyncio.locks.Semaphore,
                          session: aiohttp.client.ClientSession,
                          job_data: dict) -> dict:
        """Processes pages with semaphore

        Args:
            semaphore: Regulates the number of parallel requests
            session: AIOHttp's session object
            job_data: Data, related to concrete web-page"""

        async with semaphore:
            return await self.fetch_page(session, job_data)

    async def parse_pages(self, jobs: dict) -> None:
        """Asynchronously fetches and processes multiple pages based on the job data provided.

        Args:
            jobs: Dict with data, related to different web-pages to parse"""

        semaphore = asyncio.Semaphore(self.parallel_jobs)
        tasks = []

        async with aiohttp.ClientSession() as session:
            for job_data in jobs.values():
                task = asyncio.create_task(self.process_url(semaphore, session, job_data))
                tasks.append(task)

            completed_jobs = await asyncio.gather(*tasks)
            self.parse_data_from_html(completed_jobs)
