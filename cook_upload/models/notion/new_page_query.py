from typing import Annotated, Literal

from pydantic import Field

from .common_models import NotionModel


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

class Properties(NotionModel):
    name: TitleModel = Field(alias='Name')
    type_: SelectModel = Field(alias='Type')
    origin: SelectModel  | None = Field(alias='Origin', default=None)
    difficulty: SelectModel = Field(alias='Difficulty')
    source: RichTextModel = Field(alias='Source')


class NotionNewPage(NotionModel):
    parent: DbID
    properties: Properties
    children: list[Block] | None = None
