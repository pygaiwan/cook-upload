from datetime import datetime

from pydantic import Field, HttpUrl

from .notion_common_models import (
    Annotations,
    Icon,
    IdNameColor,
    NotionModel,
    ObjectAndId,
    Parent,
    Text,
)


class SelectModel(NotionModel):
    id_: str = Field(alias='id')
    name: str | None = None
    type_: str = Field(alias='type')
    select: IdNameColor | None = None


class RichText(NotionModel):
    type_: str = Field(alias='type')
    text: Text
    annotations: Annotations
    plain_text: str
    href: str | None = None


class RichTextModel(NotionModel):
    id_: str = Field(alias='id')
    type_: str = Field(alias='type')
    rich_text: list[RichText] | None = None
    title: list[RichText] | None = None


class Date(NotionModel):
    start: str
    time_zone: str | None = None


class DateModel(NotionModel):
    id_: str = Field(alias='id')
    type_: str = Field(alias='type')
    date: str | Date | None = None


class Properties(NotionModel):
    type_: SelectModel = Field(alias='Type')
    origin: SelectModel = Field(alias='Origin')
    difficulty: SelectModel = Field(alias='Difficulty')
    source: RichTextModel = Field(alias='Source')
    date: DateModel = Field(alias='Date')
    name: RichTextModel = Field(alias='Name')


class Result(NotionModel):
    object_: str = Field(alias='object')
    id_: str = Field(alias='id')
    created_time: datetime
    last_edited_time: datetime
    created_by: ObjectAndId
    last_edited_by: ObjectAndId
    cover: str | None = None
    icon: Icon | None = None
    parent: Parent
    archived: bool
    in_trash: bool
    properties: Properties
    url: HttpUrl
    public_url: HttpUrl | None = None


class NotionDBSearch(NotionModel):
    object_: str = Field(alias='object')
    results: list[Result]
    next_cursor: str | None = None
    has_more: bool
    type_: str = Field(alias='type')
    page_or_database: dict
    request_id: str
