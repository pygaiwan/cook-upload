from base64 import b64encode
from os import environ
from pathlib import Path
from typing import Annotated

import typer
from iso3166 import countries
from openai import OpenAI
from typer import Typer

from cook_upload.notion_actions import NotionActions

from ..constants import (
    NOTION_API_KEY,
    NOTION_DB_ID,
    OPENAI_API_KEY,
    OPENAI_PROJECT_ID,
    DishDifficulty,
)

CMD_NAME = 'upload'
CMD_HELP = 'Upload image and text to Notion'
CMD_RICH_HELP = 'Upload utility'


app = Typer(no_args_is_help=True)
openai_instance = OpenAI(
    api_key=environ.get(OPENAI_API_KEY),
    project=environ.get(OPENAI_PROJECT_ID),
)

notion_instance = NotionActions(
    api_key=environ.get(NOTION_API_KEY),
    db_id=environ.get(NOTION_DB_ID),
)


def _validate_country(origin: str) -> str:
    try:
        return countries.get(origin.lower()).name
    except KeyError as e:
        raise ValueError(f'The country {origin} is not valid') from e


def _validate_dish_type(type_: str) -> str:
    return type_


@app.command(help=CMD_HELP)
# i think origin has to be an option
def upload(
    image_path: Annotated[str, typer.Argument()],
    difficulty: Annotated[DishDifficulty, typer.Argument()],
    type_: Annotated[str, typer.Argument()],
    origin: Annotated[str, typer.Option()] = None,
):
    if origin:
        country_name = _validate_country(origin)
    dish_type = _validate_dish_type(type_)

    path = Path(image_path)
    image = b64encode(path.read_bytes()).decode('utf-8')
    # with vcr.use_cassette('baserequest.yaml'):
    #     title, ingredients, steps = parse_image(openai_instance, base64_image=image)
    # print(title)
    # print(ingredients)
    # print(steps)
    #
