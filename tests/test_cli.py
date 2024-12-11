import os
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from typer.testing import CliRunner

from cook_upload.main import app

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

IMAGE_PATH = (Path(__file__).parent / 'images' / 'image.jpg').as_posix()
MINIMAL_PARAMS = [IMAGE_PATH, 'Easy', '-s', 'Source1', '-t', 'Meat']

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
@pytest.mark.vcr
def test_app_invoke_should_error_missing_params(commands):
    results = runner.invoke(app, commands)
    assert results.exit_code == 2


@pytest.mark.vcr
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


bad_params = [
    [IMAGE_PATH, 'Easy', '-s', 'Source1', '-t', 'Meat', '-c', 'Wrong'],
    [IMAGE_PATH, 'Easy', '-s', 'Source1', '-t', 'Wrong', '-c', 'Italy'],
    [IMAGE_PATH, 'Easy', '-s', 'Source1', '-t', 'Meat', '-c', 'Italy', '-d', '20243131'],
]


@pytest.mark.parametrize('commands', bad_params, ids=['country', 'dish_type', 'date'])
@pytest.mark.vcr
def test_params_should_error(commands):
    results = runner.invoke(app, commands, env=os.environ.copy(), catch_exceptions=False)
    assert results.exit_code == 2


image_paths = [
    Path(__file__).parent / 'something.jpg',
    Path(__file__).parent,
    Path(__file__).parent / 'images' / 'image.png',
]


@pytest.mark.parametrize(
    'image_path',
    image_paths,
    ids=['image_not_exists', 'image_not_file', 'image_not_jpg'],
)
@pytest.mark.vcr
def test_params_should_error_bad_image_path(image_path):
    commands = [
        image_path.as_posix(),
        'Easy',
        '-s',
        'Leith p.56',
        '-d',
        '20241221',
        '-c',
        'Italy',
        '-t',
        'Meat',
        '-f',
    ]

    results = runner.invoke(app, commands, env=os.environ.copy(), catch_exceptions=False)
    assert results.exit_code == 2


dates = [
    (None, None),
    ('', datetime.today().strftime('%Y-%m-%d')),
    ('20241212', '2024-12-12'),
]


@pytest.mark.parametrize(('date', 'expected_date'), dates, ids=['None', 'today', 'specific_date'])
@pytest.mark.vcr
def test_date_param_is_as_expected(mocker, date, expected_date):
    commands = [IMAGE_PATH, 'Easy', '-s', 'Source1', '-t', 'Meat', '-c', 'Italy']
    expected_params = {
        'difficulty': 'Easy',
        'force': False,
        'ingredients': 'string2',
        'origin': 'Italy',
        'source': 'Source1',
        'steps': 'string3',
        'title': 'String1',
        'type_': 'Meat',
    }
    if date is not None:
        commands.extend(['-d', date])
    expected_params['date'] = expected_date

    mocker.patch('cook_upload.main.parse_image', return_value=('string1', 'string2', 'string3'))
    mocked_action = mocker.patch('cook_upload.main.notion_instance.add_entry', autospec=True)
    runner.invoke(app, commands)

    args = mocked_action.call_args
    assert dict(args[1]) == expected_params
