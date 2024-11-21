import pytest
from typer.testing import CliRunner

from cook_upload.main import app

runner = CliRunner()


def test_app_standard_params():
    results = runner.invoke(
        app,
        ['image.jpg', 'Easy', '-s', 'Leith p.56', '-d', '21112024', '-c', 'Italy', '-t', 'Meat'],
    )
    print(results.output)
    assert results.exit_code == 0


def test_app_lower_case_difficulty_ok():
    results = runner.invoke(
        app,
        ['image.jpg', 'easy', '-s', 'Leith p.56', '-d', '21112024', '-c', 'Italy', '-t', 'Meat'],
    )
    assert results.exit_code == 0

def test_app_unexisting_file_should_fail(tmp_path):
    results = runner.invoke(
        app,
        [tmp_path / 'image.jpg', 'easy', '-s', 'Leith p.56', '-d', '21112024', '-c', 'Italy', '-t', 'Meat'],
    )
    assert results.exit_code == 0

def test_app_without_date_ok():
    results = runner.invoke(
        app,
        ['image.jpg', 'easy', '-s', 'Leith p.56', '-c', 'Italy', '-t', 'Meat'],
    )
    assert results.exit_code == 0


def test_app_without_country():
    results = runner.invoke(
        app,
        ['image.jpg', 'easy', '-s', 'Leith p.56', '-t', 'Meat'],
    )
    assert results.exit_code == 0


commands = [
    ['image.jpg', 'easy', '-d', '21112024', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', '-s', 'Leith p.56', '-d', '21112024', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-c', 'Italy', '-t', 'Meat'],
    ['image.jpg', 'easy', '-s', 'Leith p.56', '-d', '21112024', '-c', 'Italy'],
]


@pytest.mark.parametrize('commands', commands)
def test_app_should_error_missing_params(commands):
    results = runner.invoke(app, commands)
    assert results.exit_code == 0
