import click

from ..config import save_config
from ..console import CONTEXT_SETTINGS, abort, echo_failure, echo_info, echo_success, echo_waiting, echo_warning
from ..gcloud import GCloud
from ..gsutil import GSUtil
from ..location import get_default_locations, get_detected_time_zones


@click.command(
    'create', context_settings=CONTEXT_SETTINGS, short_help='Create resources required to run a new instance locally'
)
@click.argument('instance_name')
@click.pass_context
def create_command(ctx, instance_name):
    """Create resources required to run a new instance locally."""
    config = ctx.obj
    instances = config['instances']
    instance_exists = instance_name in instances

    if not instance_exists and not (config['compute_zone'] and config['storage_region']):
        compute_location, storage_location = get_default_locations()
        detected_time_zones = get_detected_time_zones()

        if detected_time_zones is None:
            echo_warning(f'Auto-detection of your nearest Google Cloud data center was unsuccessful!\n')
        elif not (compute_location and storage_location):
            echo_warning(
                f'Data center auto-detection of your time zones {detected_time_zones} is not yet supported.\n'
                f'Please go to https://github.com/ofek/perplex/issues/new with this info and make a suggestion!\n'
            )

        echo_failure('You must ensure your `compute_zone` and `storage_region` are set.')
        echo_info(
            'Compute zone:\n'
            '    Command: perplex config set default.compute_zone\n'
            '    Options: https://cloud.google.com/compute/docs/regions-zones/#available\n'
            'Storage region:\n'
            '    Command: perplex config set default.storage_region\n'
            '    Options: https://cloud.google.com/storage/docs/locations#available_locations'
        )
        abort()

    if not config['project_id']:
        if not click.confirm('No `project_id` is set. Would you like to create a new Google Cloud project now?'):
            abort(
                'You must select a valid project ID from the output of `gcloud projects list`.\n'
                'Afterward, run `perplex config set default.project_id`.'
            )

        echo_waiting('Discovering available billing accounts...')
        billing_accounts = GCloud.get_billing_accounts()
        if not billing_accounts:
            abort(
                'There no available billing accounts. To create one, go to:\n'
                'https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account'
            )

        choices = {str(i): ba for i, ba in enumerate(billing_accounts, 1)}
        choice = click.prompt(
            'Which billing account should be used?\n{}'.format('\n'.join(f'  {i} - {ba}' for i, ba in choices.items())),
            prompt_suffix='\n: ',
            show_choices=False,
            show_default=False,
            type=click.Choice(list(choices)),
        )
        billing_account = billing_accounts[choices[choice]]

        echo_waiting('Creating a new Google Cloud project... ', nl=False)
        project_id = GCloud.create_project(config['project_prefix'])

        if project_id:
            config['project_id'] = project_id
            save_config(config)
            echo_success('success!')
        else:
            click.echo()
            echo_info(GCloud.last_output)
            abort('Failed!', code=GCloud.last_return_code)

        echo_waiting(f'Linking billing account `{billing_account}` to project `{project_id}`... ', nl=False)
        success = GCloud.enable_project_billing(project_id, billing_account)

        if success:
            echo_success('success!')
        else:
            click.echo()
            echo_info(GCloud.last_output)
            abort('Failed!', code=GCloud.last_return_code)

    instance = instances.setdefault(instance_name, {})

    if not instance_exists:
        config['instance'] = instance_name

        instance.setdefault('method', 'local')
        instance.setdefault('time_zone', config['time_zone'])
        instance.setdefault('image', config['image'])
        instance.setdefault('project_id', config['project_id'])
        instance.setdefault('compute_zone', config['compute_zone'])
        instance.setdefault('compute_node_type', config['compute_node_type'])
        instance.setdefault('compute_disk_type', config['compute_disk_type'])
        instance.setdefault('compute_disk_space', config['compute_disk_space'])
        instance.setdefault('bucket_media', '')
        instance.setdefault('bucket_metadata', '')
        instance.setdefault('service_account_storage', '')
        instance.setdefault('service_account_storage_policy', False)

        echo_waiting(f'Saving initial configuration for instance `{instance_name}`... ', nl=False)
        save_config(config)
        echo_success('success!')

    gsutil = GSUtil(config)

    if not instance['bucket_media']:
        echo_waiting('Creating storage for your media... ', nl=False)
        bucket_media = gsutil.create_media_bucket()

        if bucket_media:
            instance['bucket_media'] = bucket_media
            save_config(config)
            echo_success('success!')
        else:
            abort('Failed!')

    if not instance['bucket_metadata']:
        echo_waiting('Creating storage for your Plex metadata... ', nl=False)
        bucket_metadata = gsutil.create_metadata_bucket()

        if bucket_metadata:
            instance['bucket_metadata'] = bucket_metadata
            save_config(config)
            echo_success('success!')
        else:
            abort('Failed!')

    gcloud = GCloud(config, instance_name)

    if not instance['service_account_storage']:
        echo_waiting('Creating a service account for your storage... ', nl=False)
        service_account_storage = gcloud.create_storage_service_account()

        if service_account_storage:
            instance['service_account_storage'] = service_account_storage
            save_config(config)
            echo_success('success!')
        else:
            click.echo()
            echo_info(gcloud.last_output)
            abort('Failed!', code=gcloud.last_return_code)

    if not instance['service_account_storage_policy']:
        echo_waiting('Adding the access policy for the service account... ', nl=False)
        success = gcloud.create_storage_policy()

        if success:
            instance['service_account_storage_policy'] = True
            save_config(config)
            echo_success('success!')
        else:
            click.echo()
            echo_info(gcloud.last_output)
            abort('Failed!', code=gcloud.last_return_code)

    if not gcloud.storage_service_account_key_file_exists():
        echo_waiting('Creating a private key for the service account... ', nl=False)
        success = gcloud.create_storage_service_account_key_file()

        if success:
            echo_success('success!')
        else:
            click.echo()
            echo_info(gcloud.last_output)
            abort('Failed!', code=gcloud.last_return_code)

    echo_success(f'Instance `{instance_name}` is all set up! Run `perplex launch`.')
