import os

import click

from .commands import ALL_COMMANDS
from .config import CONFIG_FILE, config_file_exists, load_config, restore_config
from .console import CONTEXT_SETTINGS, echo_success, echo_waiting, echo_warning


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option()
@click.pass_context
def perplex(ctx):
    if not config_file_exists():
        echo_waiting('No config file found, creating one with default settings now...')

        try:
            restore_config()
            echo_success('Success! Check out `perplex config`.')
        except (IOError, OSError, PermissionError):
            echo_warning(f'Unable to create config file located at `{CONFIG_FILE}`. Please check your permissions.')

    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return

    # Load and store configuration for sub-commands.
    ctx.obj = load_config()

    #
    os.environ['COMPOSE_CONVERT_WINDOWS_PATHS'] = '1'


for command in ALL_COMMANDS:
    perplex.add_command(command)
