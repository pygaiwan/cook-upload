from base64 import b64encode
from os import environ
from pathlib import Path

import typer
from iso3166 import countries
from openai import OpenAI

from .constants import DishDifficulty
from .openai_actions import parse_image

app = typer.Typer()
openai_instance = OpenAI(
    api_key=environ.get('OPENAI_API_KEY'),
    project=environ.get('OPENAI_PROJECT_ID'),
)


def _validate_country(origin: str) -> str:
    try:
        return countries.get(origin.lower()).name
    except KeyError as e:
        raise ValueError(f'The country {origin} is not valid') from e


def _validate_dish_type(type_: str) -> str:
    return type_


@app.command()
# i think origin has to be an option
def upload(image_path: str, difficulty: DishDifficulty, type_: str, origin: str = None):
    if origin:
        country_name = _validate_country(origin)
    dish_type = _validate_dish_type(type_)

    path = Path(image_path)
    image = b64encode(path.read_bytes()).decode('utf-8')
    title, ingredients, steps = parse_image(openai_instance, base64_image=image)
    print(title)
    print(ingredients)
    print(steps)


if __name__ == '__main__':
    app()
