import click
import toml

from ..config import (
    CONFIG_FILE,
    SECRET_KEYS,
    config_file_exists,
    read_config_file,
    read_config_file_scrubbed,
    restore_config,
    save_config,
    scrub_secrets,
    update_config,
)
from ..console import CONTEXT_SETTINGS, abort, echo_info, echo_success
from ..utils import string_to_toml_type


@click.group('config', context_settings=CONTEXT_SETTINGS, short_help='Manage the config file')
def config_command():
    pass


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Open the config location in your file manager')
def explore():
    """Open the config location in your file manager."""
    click.launch(CONFIG_FILE, locate=True)


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Show the location of the config file')
def find():
    """Show the location of the config file."""
    if ' ' in CONFIG_FILE:
        echo_info(f'"{CONFIG_FILE}"')
    else:
        echo_info(CONFIG_FILE)


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Show the contents of the config file')
@click.option('--all', '-a', 'all_keys', is_flag=True, help='No not scrub secret fields')
def show(all_keys):
    """Show the contents of the config file."""
    if not config_file_exists():
        echo_info('No config file found! Please try `perplex config restore`.')
    else:
        if all_keys:
            echo_info(read_config_file().rstrip())
        else:
            echo_info(read_config_file_scrubbed().rstrip())


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Update the config file with any new fields')
def update():
    """Update the config file with any new fields."""
    update_config()
    echo_success('Settings were successfully updated.')


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Restore the config file to default settings')
def restore():
    """Restore the config file to default settings."""
    restore_config()
    echo_success('Settings were successfully restored.')


@config_command.command(context_settings=CONTEXT_SETTINGS, short_help='Select an instance to use')
@click.argument('instance')
@click.pass_context
def use(ctx, instance):
    """Select an instance to use."""
    user_config = ctx.obj

    if instance not in user_config['instances']:
        abort(f'Instance `{instance}` does not exist. To create one, see `perplex create -h`.')

    user_config['instance'] = instance
    save_config(user_config)


@config_command.command('set', context_settings=CONTEXT_SETTINGS, short_help='Assign values to config file entries')
@click.argument('key')
@click.argument('value', required=False)
@click.pass_context
def set_value(ctx, key, value):
    """Assigns values to config file entries. If the value is omitted,
    you will be prompted, with the input hidden if it is sensitive.
    """
    default_key = False
    if key.startswith('default.'):
        default_key = True
        key = key.split('default.', 1)[1]

    scrubbing = False
    if value is None:
        scrubbing = key in SECRET_KEYS
        value = click.prompt(f'Value for `{key}`', hide_input=scrubbing)

    user_config = ctx.obj
    if default_key:
        new_config = user_config
    else:
        instance = user_config['instance']
        instances = user_config['instances']

        if not instance:
            abort('No default instance specified. To use one, see `perplex config use -h`.')
        elif instance not in instances:
            abort(f'Instance `{instance}` does not exist. To create one, see `perplex create -h`.')

        new_config = instances[instance]

    data = [value]
    data.extend(reversed(key.split('.')))
    key = data.pop()
    value = data.pop()

    # Use a separate mapping to show only what has changed in the end
    branch_config_root = branch_config = {}

    # Consider dots as keys
    while data:
        default_branch = {value: ''}
        branch_config[key] = default_branch
        branch_config = branch_config[key]

        new_value = new_config.get(key)
        if not hasattr(new_value, 'get'):
            new_value = default_branch

        new_config[key] = new_value
        new_config = new_config[key]

        key = value
        value = data.pop()

    value = string_to_toml_type(value)
    branch_config[key] = new_config[key] = value

    save_config(user_config)

    output_config = scrub_secrets(branch_config_root) if scrubbing else branch_config_root
    echo_success('New setting:')
    echo_info(toml.dumps(output_config).rstrip())
