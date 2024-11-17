from pydantic import Field

from .common_models import Columns, NotionModel


class Result(NotionModel):
    id_: str = Field(alias='id')
    properties: Columns


class NotionDBSearch(NotionModel):
    results: list[Result]
    next_cursor: str | None = None
    has_more: bool
