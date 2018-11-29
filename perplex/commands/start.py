import click

from ..compose import DockerCompose
from ..console import CONTEXT_SETTINGS, abort, echo_waiting
from ..kubectl import Kubectl


@click.command('start', context_settings=CONTEXT_SETTINGS, short_help='Start an instance')
@click.argument('instance_name', required=False)
@click.option('--no-sync', '-n', is_flag=True, help='No not update deployments based on configuration')
@click.pass_context
def start_command(ctx, instance_name, no_sync):
    """Start an instance."""
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

    echo_waiting(f'Starting instance `{instance_name}`...')
    result = deployment.start(sync=not no_sync)
    if result.returncode:
        abort(code=result.returncode)
