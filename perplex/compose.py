import yaml

from .config import app_dir
from .constants import CONTAINER_NAME, SERVICE_ACCOUNT_STORAGE_KEY_FILE
from .utils import exe_exists, file_exists, get_docker_hostname, path_join, run_command, write_file


class DockerCompose:
    exe_name = 'docker-compose'
    file_name = 'docker-compose.yaml'

    def __init__(self, instance, instance_name):
        self.instance_name = instance_name
        self.instance = instance
        self.file_path = path_join(app_dir(self.instance_name), self.file_name)

    @classmethod
    def is_available(cls):
        return exe_exists(cls.exe_name)

    def is_active(self):
        if not file_exists(self.file_path):
            return False

        lines = run_command([self.exe_name, '-f', self.file_path, 'ps'], capture=True).stdout.splitlines()

        for i, line in enumerate(lines, 1):
            if set(line.strip()) == {'-'}:
                return len(lines[i:]) >= 1

        return False

    def get_plex_url(self):
        return f'http://{get_docker_hostname()}:32400/web'

    def start(self, sync=True):
        if sync:
            self.sync()

        return run_command([self.exe_name, '-f', self.file_path, 'up', '-d'])

    def stop(self):
        return run_command([self.exe_name, '-f', self.file_path, 'down'])

    def sync(self):
        write_file(self.file_path, yaml.safe_dump(self.derive_config(), default_flow_style=False))

    def derive_config(self):
        return {
            'version': '3',
            'services': {
                self.instance_name: {
                    'image': self.instance['image'],
                    'container_name': CONTAINER_NAME,
                    # FUSE needs device
                    'devices': ['/dev/fuse'],
                    # FUSE needs extra capabilities. See:
                    # https://github.com/s3fs-fuse/s3fs-fuse/issues/647#issuecomment-392697838
                    'cap_add': ['SYS_ADMIN'],
                    'ports': ['32400:32400'],
                    'environment': [
                        'BOTO_CONFIG=/home/.boto',
                        f'TZ={self.instance["time_zone"]}',
                        f'BUCKET_MEDIA={self.instance["bucket_media"]}',
                        f'BUCKET_METADATA={self.instance["bucket_metadata"]}',
                        f'PROJECT_ID={self.instance["project_id"]}',
                        f'GOOGLE_APPLICATION_CREDENTIALS=/home/secrets/{SERVICE_ACCOUNT_STORAGE_KEY_FILE}',
                    ],
                    'volumes': [
                        f'./{SERVICE_ACCOUNT_STORAGE_KEY_FILE}:/home/secrets/{SERVICE_ACCOUNT_STORAGE_KEY_FILE}'
                    ],
                }
            },
        }
