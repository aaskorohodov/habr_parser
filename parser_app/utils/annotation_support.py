from typing import TypedDict, Any, TypeVar
from parser_app.parsers.pasrser_interface import ParserInterface


class UpdateDict(TypedDict):
    """Explains the structure of a dict, to update a table with connector"""

    table_name: str
    where: dict[str, Any]
    data: dict[str, Any]


class InsertIgnoreDict(TypedDict):
    """Explains the structure of a dict, to insert or ignore data into a table with connector"""

    table_name: str
    data: dict[str, Any]


PARSER_INTERFACE = TypeVar('PARSER_INTERFACE', bound=ParserInterface)
