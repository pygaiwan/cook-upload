from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .common_models import Columns, NotionModel


class NotionDBMetadata(NotionModel):
    object_: str = Field(alias='object')
    id_: str = Field(alias='id')
    properties: Columns
    url: HttpUrl
