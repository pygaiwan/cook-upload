from datetime import datetime
from typing import Annotated

from typer import Argument, Option, Typer

from cook_upload.constants import DishDifficulty

app = Typer(
    no_args_is_help=True,
    rich_markup_mode='markdown',
    context_settings={'help_option_names': ['-h', '--help']},
)
TODAY = datetime.today().date().strftime('%d%m%Y')


@app.command()
def main(
    image_path: Annotated[str, Argument(help='The image name or path to process.', exists=True)],
    difficulty: Annotated[
        DishDifficulty, Argument(case_sensitive=False, help='The difficulty of the dish.'),
    ],
    source: Annotated[
        str, Option('--source', '-s', help='Source from where the receipt has been taken from'),
    ],
    country: Annotated[str, Option('--country', '-c', help='Country of origin of the receipt.')],
    type_: Annotated[str, Option('--type', '-t', help='Type of receipt')],
    date: Annotated[
        str,
        Option(
            '--date',
            '-d',
            help='Date where the receipt has been done. Example 21122024.',
        ),
    ] = TODAY,
):
    """
    Default command to handle upload if no subcommand is specified.
    """
    titled_difficulty = difficulty.value.title()
    print(titled_difficulty)
    print(image_path)
    print(source)
    print(date)
    print(country)
    print(type_)

    # upload(
    #     image_path=image_path,
    #     difficulty=difficulty,
    #     type_=type_,
    #     origin=origin,
    # )


if __name__ == '__main__':
    app()
