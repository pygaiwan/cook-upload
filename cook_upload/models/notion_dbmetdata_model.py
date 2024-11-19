from datetime import datetime

from pydantic import Field, HttpUrl

from .notion_common_models import (
    Annotations,
    Icon,
    NotionModel,
    ObjectAndId,
    Parent,
    Text,
)


class Title(NotionModel):
    type_: str = Field(alias='type')
    text: Text
    annotations: Annotations
    plain_text: str
    href: str | None = None


class Option(NotionModel):
    id_: str = Field(alias='id')
    name: str
    color: str
    description: str | None = None


class Select(NotionModel):
    options: list[Option]


class SelectModel(NotionModel):
    id_: str = Field(alias='id')
    name: str
    type_: str = Field(alias='type')
    select: Select


class SourceModel(NotionModel):
    id_: str = Field(alias='id')
    name: str
    type_: str = Field(alias='type')
    rich_text: dict


class DateModel(NotionModel):
    id_: str = Field(alias='id')
    name: str
    type_: str = Field(alias='type')
    date: dict


class NameModel(NotionModel):
    id_: str = Field(alias='id')
    name: str
    type_: str = Field(alias='type')
    title: dict


class Properties(NotionModel):
    type_: SelectModel = Field(alias='Type')
    origin: SelectModel = Field(alias='Origin')
    difficulty: SelectModel = Field(alias='Difficulty')
    source: SourceModel = Field(alias='Source')
    date: DateModel = Field(alias='Date')
    name: NameModel = Field(alias='Name')


class NotionDBMetadata(NotionModel):
    object_: str = Field(alias='object')
    id_: str = Field(alias='id')
    cover: str | None = None
    icon: Icon | None = None
    created_time: datetime
    created_by: ObjectAndId
    last_edited_by: ObjectAndId
    last_edited_time: datetime
    title: list[Title]
    description: list[str]
    is_inline: bool
    properties: Properties
    parent: Parent
    url: HttpUrl
    public_url: HttpUrl | None = None
    archived: bool
    in_trash: bool
    request_id: str
