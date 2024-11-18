from pydantic import BaseModel


class Url(BaseModel):
    url: str


class Content(BaseModel):
    type: str
    text: str | None = None
    image_url: Url | None = None


class ImageRequest(BaseModel):
    role: str = 'user'
    content: list[Content]


class ExtractionResponse(BaseModel):
    title: str
    steps: str
    ingredients: str
