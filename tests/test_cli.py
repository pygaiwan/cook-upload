import pytest
from typer.testing import CliRunner

from cook_upload.main import app

runner = CliRunner()

commands = [
    ['image.jpg', 'Easy', '-s', 'Leith p.56', '-d', '20242112', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-d', '20242112', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-t', 'Meat'],
]


@pytest.mark.parametrize(
    'commands',
    commands,
    ids=['all_params', 'lowercase_diff', 'no_date', 'no_country'],
)
@pytest.mark.vcr
def test_app_invoke_works(commands):
    results = runner.invoke(app, commands)
    assert results.exit_code == 0


commands = [
    ['image.jpg', 'easy', '-d', '20242112', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', '-s', 'Leith p.56', '-d', '20242112', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-d', '20242112', '-c', 'Italy'],
]


@pytest.mark.parametrize('commands', commands, ids=['no_source', 'no_difficulty', 'no_type'])
def test_app_invoke_should_error_missing_params(commands):
    results = runner.invoke(app, commands)
    print(results.output)
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
            '20242112',
            '-c',
            'Italy',
            '-t',
            'Meat',
        ],
    )
    assert results.exit_code == 2
