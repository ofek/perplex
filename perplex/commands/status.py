import click

from ..compose import DockerCompose
from ..console import CONTEXT_SETTINGS, abort, echo_failure, echo_info, echo_success
from ..docker import Docker
from ..gcloud import GCloud
from ..gsutil import GSUtil
from ..kubectl import Kubectl


@click.command('status', context_settings=CONTEXT_SETTINGS, short_help='Show the status of the current environment')
@click.pass_context
def status_command(ctx):
    """Show the status of the current environment."""
    failed = False

    echo_info('Tooling:')

    echo_info(f'{Docker.exe_name}: ', indent=True, nl=False)
    if Docker.is_available():
        echo_success('found')
    else:
        failed = True
        echo_failure('not found')

    echo_info(f'{DockerCompose.exe_name}: ', indent=True, nl=False)
    if DockerCompose.is_available():
        echo_success('found')
    else:
        failed = True
        echo_failure('not found')

    echo_info(f'{GCloud.exe_name}: ', indent=True, nl=False)
    if GCloud.is_available():
        echo_success('found')
    else:
        failed = True
        echo_failure('not found')

    echo_info(f'{GSUtil.exe_name}: ', indent=True, nl=False)
    if GSUtil.is_available():
        echo_success('found')
    else:
        failed = True
        echo_failure('not found')

    echo_info(f'{Kubectl.exe_name}: ', indent=True, nl=False)
    if Kubectl.is_available():
        echo_success('found')
    else:
        failed = True
        echo_failure('not found. Try `gcloud components install kubectl`.')

    echo_info('\nInstance:')

    config = ctx.obj
    instance = config['instance']
    instances = config['instances']

    if not instance:
        failed = True
        echo_failure('error: No default instance specified. To use one, see `perplex config use -h`.', indent=True)
    elif instance not in instances:
        failed = True
        echo_failure(
            f'error: Instance `{instance}` does not exist. To create one, see `perplex create -h`.', indent=True
        )
    else:
        echo_info('name: ', indent=True, nl=False)
        echo_success(instance)

    if failed:
        abort()
