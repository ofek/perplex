import webbrowser

import click

from ..compose import DockerCompose
from ..console import CONTEXT_SETTINGS, abort, echo_waiting
from ..kubectl import Kubectl
from ..utils import wait_for_endpoints


@click.command('launch', context_settings=CONTEXT_SETTINGS, short_help='Open Plex in a web browser')
@click.argument('instance_name', required=False)
@click.pass_context
def launch_command(ctx, instance_name):
    """Open Plex in a web browser."""
    config = ctx.obj
    if not instance_name:
        instance_name = config['instance']

    instance = config['instances'].get(instance_name)

    if not instance:
        abort(f'Instance `{instance_name}` does not exist. To create one, see `perplex create -h`.')

    if instance['method'] == 'local':
        deployment = DockerCompose(instance, instance_name)
    else:
        deployment = Kubectl(instance, instance_name)

    if not deployment.is_active():
        echo_waiting(f'Starting instance `{instance_name}`...')
        result = deployment.start()
        if result.returncode:
            abort(code=result.returncode)

    echo_waiting(f'Waiting for instance `{instance_name}`...')
    url = deployment.get_plex_url()
    wait_for_endpoints([url])

    webbrowser.open_new_tab(url)
