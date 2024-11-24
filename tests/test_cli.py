import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from typer.testing import CliRunner

from cook_upload.main import app

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

IMAGE_PATH = (Path(__file__).parent / 'images' / 'image.jpg').as_posix()
runner = CliRunner()

commands = [
    [IMAGE_PATH, 'Easy', '-s', 'Leith p.56', '-d', '20241221', '-c', 'Italy', '-t', 'Meat', '-f'],
    [IMAGE_PATH, 'easy', '-s', 'Leith p.56', '-d', '20241221', '-c', 'Italy', '-t', 'Meat', '-f'],
    [IMAGE_PATH, 'easy', '-s', 'Leith p.56', '-c', 'Italy', '-t', 'Meat', '-f'],
    [IMAGE_PATH, 'easy', '-s', 'Leith p.56', '-t', 'Meat', '-f'],
]


@pytest.mark.parametrize(
    'commands',
    commands,
    ids=['all_params', 'lowercase_diff', 'no_date', 'no_country'],
)
@pytest.mark.vcr
def test_app_invoke_works(commands, mocker):
    mocker.patch('cook_upload.main.parse_image', return_value=('string1', 'string2', 'string3'))
    results = runner.invoke(app, commands, env=os.environ.copy(), catch_exceptions=False)
    assert results.exit_code == 0


commands = [
    [IMAGE_PATH, 'easy', '-d', '20241221', '-c', 'Italy', '-t', 'Meat'],
    [IMAGE_PATH, '-s', 'Leith p.56', '-d', '20241221', '-c', 'Italy', '-t', 'Meat'],
    [IMAGE_PATH, 'easy', '-s', 'Leith p.56', '-d', '20241221', '-c', 'Italy'],
]


@pytest.mark.parametrize('commands', commands, ids=['no_source', 'no_difficulty', 'no_type'])
def test_app_invoke_should_error_missing_params(commands):
    results = runner.invoke(app, commands)
    assert results.exit_code == 2


def test_app_unexisting_file_should_fail(tmp_path):
    results = runner.invoke(
        app,
        [
            (tmp_path / 'image.jpg').as_posix(),
            'easy',
            '-s',
            'Leith p.56',
            '-d',
            '20241221',
            '-c',
            'Italy',
            '-t',
            'Meat',
        ],
    )
    assert results.exit_code == 2
