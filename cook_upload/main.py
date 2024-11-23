import mimetypes
import sys
from base64 import b64encode
from datetime import datetime
from os import environ
from pathlib import Path
from typing import Annotated

import vcr
from iso3166 import countries
from openai import OpenAI
from typer import Argument, BadParameter, Option, Typer

from .constants import (
    DATETIME_FORMATTED,
    DATETIME_STR,
    NOTION_API_KEY,
    NOTION_DB_ID,
    OPENAI_API_KEY,
    OPENAI_PROJECT_ID,
    DishDifficulty,
)
from .logger import logger
from .notion_actions import NotionActions
from .openai_actions import parse_image

app = Typer(
    no_args_is_help=True,
    rich_markup_mode='markdown',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_enable=False,
)

openai_instance = OpenAI(
    api_key=environ.get(OPENAI_API_KEY),
    project=environ.get(OPENAI_PROJECT_ID),
)

notion_instance = NotionActions(
    api_key=environ.get(NOTION_API_KEY),
    db_id=environ.get(NOTION_DB_ID),
)


def _validate_country(country: str | None) -> str | None:
    if not country:
        return
    try:
        return countries.get(country.lower()).name
    except KeyError as e:
        msg = f'The country {country} is not valid'
        logger.error(msg)
        raise BadParameter(msg) from e


def _validate_dish_type(type_: str) -> str:
    """This is meant to validate that the type is one of those allowed in Notion"""
    # i need to read the DBMetadata and get all the types
    return type_


def _validate_image(image_path: Path) -> Path:
    if (
        not image_path.exists()
        or not image_path.is_file()
        or 'image/jpeg' not in mimetypes.guess_type(image_path)
    ):
        msg = f"The file '{image_path}' does not exist or is not a valid file."
        logger.error(msg)
        raise BadParameter(msg)
    return image_path


def _validate_date(date: str | None) -> str | None:
    match date:
        case None:
            return None
        case '':
            return datetime.today().date().strftime(DATETIME_STR)
        case _:
            try:
                return datetime.strptime(date, DATETIME_STR).strftime(DATETIME_FORMATTED)
            except ValueError as e:
                msg = f'Date {date} does not match the correct format of YYYYMMDD'
                logger.error(msg)
                raise BadParameter(msg) from e


@app.command()
def main(
    image_path: Annotated[
        Path,
        Argument(
            help='The image name or path to process.',
            exists=True,
            readable=True,
            callback=_validate_image,
        ),
    ],
    difficulty: Annotated[
        DishDifficulty,
        Argument(case_sensitive=False, help='The difficulty of the dish.'),
    ],
    source: Annotated[
        str,
        Option('--source', '-s', help='Source from where the receipt has been taken from.'),
    ],
    type_: Annotated[
        str,
        Option(
            '--type',
            '-t',
            help='Type of receipt',
            callback=_validate_dish_type,
        ),
    ],
    country: Annotated[
        str,
        Option(
            '--country',
            '-c',
            help='Country of origin of the receipt.',
            callback=_validate_country,
        ),
    ] = None,
    date: Annotated[
        str,
        Option(
            '--date',
            '-d',
            help='Date where the receipt has been done. Example 20241231.',
            callback=_validate_date,
        ),
    ] = None,
    force: Annotated[
        bool,
        Option('--force', '-f', help='Force the name duplication if a title is already present'),
    ] = False,
):
    titled_difficulty = difficulty.value.title()
    source = source.title()

    image = b64encode(image_path.read_bytes()).decode('utf-8')
    with vcr.use_cassette('baserequest.yaml'):
        title, ingredients, steps = parse_image(openai_instance, base64_image=image)

    notion_instance.add_entry(
        title=title,
        difficulty=titled_difficulty,
        type_=type_,
        origin=country,
        date=date,
        source=source,
        ingredients=ingredients,
        steps=steps,
        force=force,
    )


if __name__ == '__main__':
    app()
