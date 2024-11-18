from pydantic import Field, HttpUrl

from .notion_common_models import Block, Columns, DbID, NotionModel


class Result(NotionModel):
    id_: str = Field(alias='id')
    properties: Columns
    url: HttpUrl


class NotionDBSearch(NotionModel):
    results: list[Result]
    next_cursor: str | None = None
    has_more: bool


class NotionDBMetadata(NotionModel):
    object_: str = Field(alias='object')
    id_: str = Field(alias='id')
    properties: Columns
    url: HttpUrl


class NotionNewPage(NotionModel):
    parent: DbID
    properties: Columns
    children: list[Block] | None = None
