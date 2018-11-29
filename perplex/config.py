from collections import deque

import toml
from appdirs import user_data_dir
from atomicwrites import atomic_write

from .constants import LATEST_IMAGE
from .location import DEFAULT_TIME_ZONE, get_default_locations, get_time_zone
from .utils import ensure_parent_dir_exists, file_exists, path_join, read_file

APP_DIR = user_data_dir('perplex', '')
INSTANCES_DIR = path_join(APP_DIR, 'instances')
CONFIG_FILE = path_join(APP_DIR, 'config.toml')

SECRET_KEYS = {}


def app_dir(instance_name):
    return path_join(INSTANCES_DIR, instance_name)


def default_config():
    compute_location, storage_location = get_default_locations()

    return {
        # time_zone is only used by Plex itself and we only actually derive
        # this during restore_config() as it is a potentially expensive call.
        'time_zone': DEFAULT_TIME_ZONE,
        'image': LATEST_IMAGE,
        'project_id': '',
        'project_prefix': 'perplex',
        'compute_zone': compute_location,
        'compute_node_type': 'n1-highcpu-4',
        'compute_disk_type': 'local-ssd',
        'compute_disk_space': 100,
        'storage_region': storage_location,
        'storage_class': 'regional',
        'storage_media_bucket_prefix': 'media',
        'storage_metadata_bucket_prefix': 'metadata',
        'storage_service_account_prefix': 'storage',
        'instance': '',
        'instances': {},
    }


def get_instance_dir(instance_name):
    return path_join(INSTANCES_DIR, instance_name)


def config_file_exists():
    return file_exists(CONFIG_FILE)


def save_config(config):
    ensure_parent_dir_exists(CONFIG_FILE)
    with atomic_write(CONFIG_FILE, mode='wb', overwrite=True) as f:
        f.write(toml.dumps(config).encode('utf-8'))


def load_config(sync=True):
    config = default_config() if sync else {}

    try:
        config.update(toml.loads(read_config_file()))
    except FileNotFoundError:
        pass

    return config


def read_config_file():
    return read_file(CONFIG_FILE)


def read_config_file_scrubbed():
    return toml.dumps(scrub_secrets(load_config(sync=False)))


def restore_config():
    config = default_config()

    # We only try to get the Olson time zone during the first run (or any
    # subsequent restoration) because it is a potentially costly operation,
    # especially on Windows since it queries the registry.
    config['time_zone'] = get_time_zone()

    save_config(config)
    return config


def update_config():
    config = default_config()
    config.update(load_config())
    save_config(config)
    return config


def scrub_secrets(config):
    _scrub_secrets(config)

    for instance_config in config['instances']:
        _scrub_secrets(instance_config)

    return config


def _scrub_secrets(config):
    for secret_key in SECRET_KEYS:
        branch = config
        paths = deque(secret_key.split('.'))

        while paths:
            path = paths.popleft()
            if not hasattr(branch, 'get'):
                break

            if path in branch:
                if not paths:
                    old_value = branch[path]
                    if isinstance(old_value, str):
                        branch[path] = '*' * len(old_value)
                else:
                    branch = branch[path]
            else:
                break

    return config
