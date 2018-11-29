from .utils import exe_exists, merge_output, run_command


class GSUtil:
    exe_name = 'gsutil'
    retry_attempts = 5
    bucket_alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    last_output = ''
    last_return_code = 1

    def __init__(self, config, instance_name=None):
        self.instance_name = instance_name
        self.config = config
        self.instance = self.config['instances'].get(instance_name, {})

    @classmethod
    def is_available(cls):
        return exe_exists(cls.exe_name)

    @classmethod
    def get_new_bucket_name(cls, prefix):
        from secrets import choice

        return f'{prefix}-{"".join(choice(cls.bucket_alphabet) for _ in range(8))}'

    def create_media_bucket(self):
        return self.create_bucket(self.config['storage_media_bucket_prefix'])

    def create_metadata_bucket(self):
        return self.create_bucket(self.config['storage_metadata_bucket_prefix'])

    def create_bucket(self, prefix):
        project_id = self.config['project_id']
        storage_class = self.config['storage_class']
        storage_region = self.config['storage_region']

        for _ in range(self.retry_attempts):
            bucket_name = self.get_new_bucket_name(prefix)
            result = run_command(
                ['gsutil', 'mb', '-p', project_id, '-c', storage_class, '-l', storage_region, f'gs://{bucket_name}'],
                capture=True,
            )
            self.last_output = merge_output(result)
            self.last_return_code = result.returncode

            if not result.returncode:
                return bucket_name
