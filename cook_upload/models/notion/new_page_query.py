from typing import Annotated, Literal

from pydantic import Field

from .common_models import NotionModel


class DbID(NotionModel):
    database_id: str


class Title(NotionModel):
    content: str


class Name(NotionModel):
    title: list[Title]


class Properties(NotionModel):
    name: Name = Field(alias='Name')


class TextContent(NotionModel):
    content: str


class RichTextItem(NotionModel):
    type_: str = Field(alias='type')
    text: TextContent


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


class NewQueryModel(NotionModel):
    parent: DbID
    properties: Properties
    children: list[Block]
