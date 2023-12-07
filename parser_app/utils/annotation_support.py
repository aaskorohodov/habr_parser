from typing import TypedDict, Any


class UpdateDict(TypedDict):
    """Explains the structure of a dict, to update a table with connector"""

    table_name: str
    where: dict[str, Any]
    data: dict[str, Any]
