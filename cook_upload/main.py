import importlib
import os
from collections import namedtuple
from pathlib import Path

import typer

Command = namedtuple('Command', ['cmd', 'name', 'cmd_help', 'cmd_rich_help'])

PKG_NAME = __name__.split('.')[0]
CMD_FOLDER = (Path(__file__).parent / 'commands').absolute()


def get_commands() -> list[Command]:
    commands = []
    for filename in os.listdir(CMD_FOLDER):
        if filename.endswith('.py') and filename.startswith('cmd_'):
            module_name = filename[:-3]
            module = importlib.import_module(f'.commands.{module_name}', package=PKG_NAME)
            commands.append(
                Command(
                    module.app,
                    module.CMD_NAME,
                    module.CMD_HELP,
                    module.CMD_RICH_HELP,
                ),
            )

    return commands


app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode='markdown',
    context_settings={'help_option_names': ['-h', '--help']},
)

for command in get_commands():
    app.add_typer(
        command.cmd,
        name=command.name,
        help=command.cmd_help,
        rich_help_panel=command.cmd_rich_help,
    )


@app.callback(invoke_without_command=True)
def main():
    pass


app()
