import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Annotated

from iso3166 import countries
from typer import Argument, BadParameter, Option, Typer

from .constants import DATETIME_FORMATTED, DATETIME_STR, DishDifficulty
from .upload import upload

app = Typer(
    no_args_is_help=True,
    rich_markup_mode='markdown',
    context_settings={'help_option_names': ['-h', '--help']},
)


def _validate_country(country: str) -> str:
    try:
        return countries.get(country.lower()).name
    except KeyError as e:
        raise BadParameter(f'The country {country} is not valid') from e


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
        raise BadParameter(f"The file '{image_path}' does not exist or is not a valid file.")
    return image_path


def _validate_date(date: str | None) -> str | None:
    match date:
        case None:
            return None
        case '':
            return datetime.today().date().strftime(DATETIME_STR)
        case _:
            return datetime.strptime(date, DATETIME_STR).strftime(DATETIME_FORMATTED)


@app.command()
def main(
    image_path: Annotated[
        Path,
        Argument(help='The image name or path to process.', exists=True, readable=True),
    ],
    difficulty: Annotated[
        DishDifficulty,
        Argument(case_sensitive=False, help='The difficulty of the dish.'),
    ],
    source: Annotated[
        str,
        Option('--source', '-s', help='Source from where the receipt has been taken from.'),
    ],
    type_: Annotated[str, Option('--type', '-t', help='Type of receipt')],
    country: Annotated[
        str,
        Option('--country', '-c', help='Country of origin of the receipt.'),
    ] = None,
    date: Annotated[
        str,
        Option(
            '--date',
            '-d',
            help='Date where the receipt has been done. Example 21122024.',
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
    if country:
        country = _validate_country(country)

    type_ = _validate_dish_type(type_)
    image_path = _validate_image(image_path)

    upload(
        image_path=image_path,
        difficulty=titled_difficulty,
        type_=type_,
        country=country,
        source=source,
        date=date,
        force=force,
    )


if __name__ == '__main__':
    app()
