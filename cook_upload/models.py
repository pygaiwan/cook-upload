from pydantic import BaseModel, ConfigDict, Field, HttpUrl



class IdName(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id_: str = Field(alias='id')
    name: str


class ColumnOptions(BaseModel):
    options: list[IdName]


class Column(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    type_: str = Field(alias='type')

    select: ColumnOptions


class SimpleColumn(BaseModel):
    name: str
    type_: str = Field(alias='type')


class Columns(BaseModel):
    type_: Column = Field(alias='Type')
    origin: Column = Field(alias='Origin')
    difficulty: Column = Field(alias='Difficulty')
    source: SimpleColumn = Field(alias='Source')
    date: SimpleColumn = Field(alias='Date')
    name: SimpleColumn = Field(alias='Name')


class NotionDBMetadata(BaseModel):
    model_config = ConfigDict(extra='ignore')

    object_: str = Field(alias='object')
    id_: str = Field(alias='id')
    properties: Columns
    url: HttpUrl
