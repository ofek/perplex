import click

from ..compose import DockerCompose
from ..console import CONTEXT_SETTINGS, abort, echo_waiting
from ..kubectl import Kubectl


@click.command('stop', context_settings=CONTEXT_SETTINGS, short_help='Stop an instance')
@click.argument('instance_name', required=False)
@click.pass_context
def stop_command(ctx, instance_name):
    """Stop an instance."""
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

    echo_waiting(f'Stopping instance `{instance_name}`...')
    result = deployment.stop()
    if result.returncode:
        abort(code=result.returncode)
