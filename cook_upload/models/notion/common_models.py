from pydantic import BaseModel, ConfigDict, Field


class NotionModel(BaseModel):
    model_config = ConfigDict(extra='ignore')


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
    plain_text: str


class NameColumn(NotionModel):
    type_: str = Field(alias='type')
    title: list[Title] | dict | None = None


class Columns(NotionModel):
    type_: Column = Field(alias='Type')
    origin: Column = Field(alias='Origin')
    difficulty: Column = Field(alias='Difficulty')
    source: SimpleColumn = Field(alias='Source')
    date: SimpleColumn = Field(alias='Date')
    name: NameColumn = Field(alias='Name')
