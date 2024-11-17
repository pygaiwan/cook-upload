from pydantic import Field, HttpUrl

from .common_models import Columns, NotionModel


class Result(NotionModel):
    id_: str = Field(alias='id')
    properties: Columns
    url: HttpUrl


class NotionDBSearch(NotionModel):
    results: list[Result]
    next_cursor: str | None = None
    has_more: bool
