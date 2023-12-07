import asyncio
from abc import ABC, abstractmethod

import aiohttp


class ParserInterface(ABC):
    @abstractmethod
    def __init__(self):
        self.logger = None
        self.parser_name = ''

    @abstractmethod
    def parse_data_from_html(self, html_pages):
        """"""

        pass

    async def fetch_page(self, session, job_data: dict) -> dict:
        """"""

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

    async def process_url(self, semaphore, session, job_data: dict):
        """"""

        async with semaphore:
            return await self.fetch_page(session, job_data)

    async def parse_pages(self, jobs: dict):
        """"""

        semaphore = asyncio.Semaphore(5)  # Control concurrency: allow up to 5 tasks at a time
        tasks = []

        async with aiohttp.ClientSession() as session:
            for job_data in jobs.values():
                task = asyncio.create_task(self.process_url(semaphore, session, job_data))
                tasks.append(task)

            completed_jobs = await asyncio.gather(*tasks)
            self.parse_data_from_html(completed_jobs)
