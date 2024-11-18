from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotionModel(BaseModel):
    model_config = ConfigDict(extra='allow')


class IdName(NotionModel):
    id_: str = Field(alias='id')
    name: str


class ColumnOptions(NotionModel):
    options: list[IdName] | None = None


class Column(NotionModel):
    name: str | dict | None = None
    type_: str = Field(alias='type')

    select: ColumnOptions | None = None


class SimpleColumn(NotionModel):
    name: str | None = None
    type_: str = Field(alias='type')


class Title(NotionModel):
    plain_text: str = ''


class NameColumn(NotionModel):
    type_: str = Field(alias='type')
    title: list[Title] = Field(default_factory=list[Title])

    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, title):
        if title == {}:
            return [Title(plain_text='')]
        return title


class DbID(NotionModel):
    database_id: str


class ContentModel(NotionModel):
    content: str


class TextModel(NotionModel):
    text: ContentModel


class TitleModel(NotionModel):
    title: list[TextModel]


class NameModel(NotionModel):
    name: str


class SelectModel(NotionModel):
    select: NameModel


class RichTextModel(NotionModel):
    rich_text: list[TextModel]


class RichTextItem(NotionModel):
    type_: str = Field(alias='type')
    text: TextModel


class HeadingContent(NotionModel):
    rich_text: list[RichTextItem]


class Heading1Block(NotionModel):
    object_: str = Field(alias='object')
    type_: Literal['heading_1'] = Field(alias='type')
    heading_1: HeadingContent


class Heading2Block(NotionModel):
    object_: str = Field(alias='object')
    type_: Literal['heading_2'] = Field(alias='type')
    heading_2: HeadingContent


class ParagraphBlock(NotionModel):
    object_: str = Field(alias='object')
    type_: Literal['paragraph'] = Field(alias='type')
    paragraph: HeadingContent


Block = Annotated[
    Heading1Block | Heading2Block | ParagraphBlock,
    Field(discriminator='type_'),
]


class Columns(NotionModel):
    type_: Column | SelectModel = Field(alias='Type')
    origin: Column | SelectModel | None = Field(alias='Origin', default=None)
    difficulty: Column | SelectModel = Field(alias='Difficulty')
    source: SimpleColumn | RichTextModel = Field(alias='Source')
    # date i dont think has to be optional. i think i need to map it everywhere
    # everywhere i mean NotionNewPage
    date: SimpleColumn | None = Field(alias='Date', default=None)
    name: NameColumn | TitleModel = Field(alias='Name')
