import sys
from textwrap import indent as __indent_text

import click

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}
UNKNOWN_OPTIONS = {'help_option_names': [], 'ignore_unknown_options': True}
DEFAULT_INDENT = 4


def indent_text(text, indent):
    return __indent_text(text, ' ' * (DEFAULT_INDENT if indent is True else indent))


def echo_info(text, nl=True, err=False, indent=None):
    if indent:
        text = indent_text(text, indent)
    click.secho(text, bold=True, nl=nl, err=err)


def echo_success(text, nl=True, err=False, indent=None):
    if indent:
        text = indent_text(text, indent)
    click.secho(text, fg='cyan', bold=True, nl=nl, err=err)


def echo_failure(text, nl=True, err=False, indent=None):
    if indent:
        text = indent_text(text, indent)
    click.secho(text, fg='red', bold=True, nl=nl, err=err)


def echo_warning(text, nl=True, err=False, indent=None):
    if indent:
        text = indent_text(text, indent)
    click.secho(text, fg='yellow', bold=True, nl=nl, err=err)


def echo_waiting(text, nl=True, err=False, indent=None):
    if indent:
        text = indent_text(text, indent)
    click.secho(text, fg='magenta', bold=True, nl=nl, err=err)


def abort(text=None, code=1, out=False):
    if text is not None:
        click.secho(text, fg='red', bold=True, err=not out)
    sys.exit(code)
