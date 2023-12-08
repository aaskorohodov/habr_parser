"""Factory that can select an appropriate parser"""


from __future__ import annotations
from typing import TYPE_CHECKING, Type

from parser_app.parsers.articles_parser.a_parser import ArticleParser
from parser_app.parsers.habs_parser.h_parser import HabsParser


if TYPE_CHECKING:
    from parser_app.utils.annotation_support import PARSER_INTERFACE


class ParserFactory:
    """Factory that can select an appropriate parser

    Attributes:
        __parsers: Collection with registered parsers"""

    __parsers = {
            'habrs': HabsParser,
            'articles': ArticleParser
        }

    @staticmethod
    def get_parser(task: str) -> Type[PARSER_INTERFACE] | LookupError:
        """Selects a parser for a required tasks

        Args:
            task: String, representing required parser
        Returns:
            Selected parser or LookupError, in case there is no requested parser"""

        selected_parser = ParserFactory.__parsers.get(task, None)
        if not selected_parser:
            selected_parser = LookupError(f'Parser for task "{task}" does not exist!')

        return selected_parser
