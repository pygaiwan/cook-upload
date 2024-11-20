from typing import Annotated, Literal

from pydantic import Field

from .notion_common_models import NotionModel


class Parent(NotionModel):
    database_id: str


class Content(NotionModel):
    content: str


class Title(NotionModel):
    text: Content


class NameModel(NotionModel):
    title: list[Title]


class Select(NotionModel):
    name: str


class SelectModel(NotionModel):
    select: Select


class RichText(NotionModel):
    type_: str | None = None
    text: Content


class SourceModel(NotionModel):
    rich_text: list[RichText]

# TODO remove None on Date. Must be mandatory
# NOTE, Origin is not mandatory
class Properties(NotionModel):
    type_: SelectModel = Field(alias='Type')
    origin: SelectModel | None = Field(alias='Origin', default=None)
    difficulty: SelectModel = Field(alias='Difficulty')
    source: SourceModel = Field(alias='Source')
    date: str | None = Field(alias='Date', default=None)
    name: NameModel = Field(alias='Name')


class HeadingContent(NotionModel):
    rich_text: list[RichText]


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


# TODO remove None from child. Must be mandatory
class NotionNewPage(NotionModel):
    parent: Parent
    properties: Properties
    children: list[Block] | None = None
