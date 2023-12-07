from __future__ import annotations
from typing import TYPE_CHECKING

from parser_app.parsers.articles_parser.a_parser import ArticleParser
from parser_app.parsers.habs_parser.h_parser import HabsParser


if TYPE_CHECKING:
    from parser_app.parsers.pasrser_interface import ParserInterface


class ParserFactory:
    __parsers = {
            'habs': HabsParser,
            'articles': ArticleParser
        }

    @staticmethod
    def get_parser(task: str) -> ParserInterface | LookupError:
        """"""

        selected_parser = ParserFactory.__parsers.get(task, None)
        if not selected_parser:
            selected_parser = LookupError(f'Parser for task "{task}" does not exist!')

        return selected_parser
