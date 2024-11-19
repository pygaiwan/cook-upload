from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class NotionModel(BaseModel):
    model_config = ConfigDict(extra='allow')


class ObjectAndId(NotionModel):
    object_: str = Field(alias='object')
    id_: str = Field(alias='id')


class Icon(NotionModel):
    type_: str = Field(alias='type')
    emoji: str


class Parent(NotionModel):
    type_: str = Field(alias='type')
    page_id: str | None = None


class IdNameColor(NotionModel):
    id_: str = Field(alias='id')
    name: str
    color: str


class Url(NotionModel):
    url: HttpUrl


class Text(NotionModel):
    content: str
    link: HttpUrl | Url | None = None


class Annotations(NotionModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str
