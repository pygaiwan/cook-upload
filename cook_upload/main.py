import mimetypes
from base64 import b64encode
from datetime import datetime
from json import dumps
from os import environ
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
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

load_dotenv(Path(__file__).parent.parent / '.env', override=False)


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
    """
    Validates the given country name.

    Args:
        country (str | None): The country name to validate.

    Returns:
        str | None: The standardized country name if valid, otherwise None.

    Raises:
        BadParameter: If the country is not a valid ISO3166 country.
    """
    if not country:
        return
    try:
        return countries.get(country.lower()).name
    except KeyError as e:
        msg = f'The country {country} is not valid'
        logger.error(msg)
        raise BadParameter(msg) from e


def _validate_dish_type(type_: str) -> str:
    """
    Validates the dish type to ensure it matches allowed values in Notion.

    Args:
        type_ (str): The type of dish to validate.

    Returns:
        str: The validated dish type.
    """
    valid_types = notion_instance.dish_type
    if type_.lower() not in valid_types:
        msg = f'The type {type_} is not allowed. The valid types are {dumps(sorted(valid_types), indent=4)}. Add it in Notion first.'
        logger.error(msg)
        raise BadParameter(msg)
    return type_.title()


def _validate_image(image_path: Path) -> Path:
    """
    Validates the provided image path to ensure it exists and is a valid JPEG image.

    Args:
        image_path (Path): The path to the image file.

    Returns:
        Path: The validated image path.

    Raises:
        BadParameter: If the file does not exist or is not a valid JPEG image.
    """
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
    """
    Validates the date string and formats it if valid.

    Args:
        date (str | None): The date to validate in YYYYMMDD format.

    Returns:
        str | None: The formatted date if valid, otherwise None.

    Raises:
        BadParameter: If the date does not match the expected format.
    """
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
    """
    Main command to process an image and add an entry to the Notion database.

    Args:
        image_path (Path): The path to the image file to be processed.
        difficulty (DishDifficulty): The difficulty of the dish.
        source (str): The source of the recipe.
        type_ (str): The type of the recipe.
        country (str, optional): The country of origin of the recipe.
        date (str, optional): The date of creation of the recipe in YYYYMMDD format.
        force (bool, optional): If True, allows adding a recipe even if a duplicate title exists.
    """
    titled_difficulty = difficulty.value.title()
    source = source.title()

    image = b64encode(image_path.read_bytes()).decode('utf-8')

    params = {
        'difficulty': titled_difficulty,
        'type_': type_,
        'origin': country,
        'date': date,
        'source': source,
        'force': force,
    }
    logger.info(f'Parameters used:\n{dumps(params, indent=4)}')
    logger.info('Starting page extraction')
    title, ingredients, steps = parse_image(openai_instance, base64_image=image)

    params['title'] = title.title()
    params['ingredients'] = ingredients
    params['steps'] = steps
    logger.info('GPT returned with:')
    logger.info(f'\tTitle: {title}')
    logger.info(f'\tIngredients:\n{ingredients}')
    logger.info(f'\tSteps:\n{steps}')
    notion_instance.add_entry(**params)


if __name__ == '__main__':
    app()
