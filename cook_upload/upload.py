from base64 import b64encode
from datetime import datetime
from os import environ
from pathlib import Path

import vcr
from openai import OpenAI

from cook_upload.models.notion_dbnewpage_model import NotionNewPage

from .constants import (
    NOTION_API_KEY,
    NOTION_DB_ID,
    OPENAI_API_KEY,
    OPENAI_PROJECT_ID,
)
from .notion_actions import NotionActions
from .openai_actions import parse_image

openai_instance = OpenAI(
    api_key=environ.get(OPENAI_API_KEY),
    project=environ.get(OPENAI_PROJECT_ID),
)

notion_instance = NotionActions(
    api_key=environ.get(NOTION_API_KEY),
    db_id=environ.get(NOTION_DB_ID),
)


def upload(
    image_path: Path,
    difficulty: str,
    type_: str,
    country: str,
    source: str,
    date:str,
    force: bool
):
    print(locals())
    image = b64encode(image_path.read_bytes()).decode('utf-8')
    with vcr.use_cassette('baserequest.yaml'):
        title, ingredients, steps = parse_image(openai_instance, base64_image=image)

    notion_instance.add_entry(
        title=title,
        difficulty=difficulty,
        type_=type_,
        origin=country,
        date=date,
        source=source,
        ingredients=ingredients,
        steps=steps,
        force=force,
    )
