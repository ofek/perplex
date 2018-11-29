from os import urandom

from .config import app_dir
from .constants import SERVICE_ACCOUNT_STORAGE_KEY_FILE
from .utils import ensure_parent_dir_exists, exe_exists, file_exists, merge_output, path_join, run_command


class GCloud:
    exe_name = 'gcloud'
    retry_attempts = 5
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
    def get_new_project_id(cls, project_prefix):
        return f'{project_prefix}-{int.from_bytes(urandom(2), "big")}'

    @classmethod
    def get_billing_accounts(cls):
        import json

        result = run_command([cls.exe_name, 'beta', 'billing', 'accounts', 'list', '--format', 'json'], capture=True)

        # [{'displayName': 'My Billing Account', 'name': 'billingAccounts/xxxxxx-xxxxxx-xxxxxx', 'open': True}, ...]
        billing_accounts = json.loads(result.stdout or '[]')

        return {ba['displayName']: ba['name'].split('/')[-1] for ba in billing_accounts}

    @classmethod
    def enable_project_billing(cls, project_id, billing_id):
        for _ in range(cls.retry_attempts):
            result = run_command(
                [cls.exe_name, 'beta', 'billing', 'projects', 'link', project_id, '--billing-account', billing_id],
                capture=True,
            )
            cls.last_output = merge_output(result)
            cls.last_return_code = result.returncode

            if not result.returncode:
                return True

    @classmethod
    def create_project(cls, project_prefix):
        for _ in range(cls.retry_attempts):
            project_id = cls.get_new_project_id(project_prefix)
            result = run_command(
                [cls.exe_name, 'projects', 'create', project_id, '--name', project_prefix], capture=True
            )
            cls.last_output = merge_output(result)
            cls.last_return_code = result.returncode

            if not result.returncode:
                return project_id

    @property
    def storage_service_account_key_file(self):
        return path_join(app_dir(self.instance_name), SERVICE_ACCOUNT_STORAGE_KEY_FILE)

    def storage_service_account_key_file_exists(self):
        return file_exists(self.storage_service_account_key_file)

    def create_storage_service_account(self):
        import json

        for _ in range(self.retry_attempts):
            service_account = f'{self.instance_name}-storage-{int.from_bytes(urandom(2), "big")}'
            result = run_command(
                [
                    self.exe_name,
                    'iam',
                    'service-accounts',
                    'create',
                    service_account,
                    '--display-name',
                    self.instance_name,
                    '--format',
                    'json',
                    '--project',
                    self.instance['project_id'],
                ],
                capture=True,
            )
            self.last_output = merge_output(result)
            self.last_return_code = result.returncode

            if not result.returncode:
                j = result.stdout

                if not j.startswith('{'):
                    # First line is not JSON
                    j = ''.join(result.stdout.splitlines(True)[1:])

                return json.loads(j)['email']

    def create_storage_policy(self):
        for _ in range(self.retry_attempts):
            result = run_command(
                [
                    self.exe_name,
                    'projects',
                    'add-iam-policy-binding',
                    self.instance['project_id'],
                    '--member',
                    f'serviceAccount:{self.instance["service_account_storage"]}',
                    '--role',
                    'roles/storage.admin',
                ],
                capture=True,
            )
            self.last_output = merge_output(result)
            self.last_return_code = result.returncode

            if not result.returncode:
                return True

    def create_storage_service_account_key_file(self):
        ensure_parent_dir_exists(self.storage_service_account_key_file)

        for _ in range(self.retry_attempts):
            result = run_command(
                [
                    self.exe_name,
                    'iam',
                    'service-accounts',
                    'keys',
                    'create',
                    self.storage_service_account_key_file,
                    '--iam-account',
                    self.instance['service_account_storage'],
                    '--project',
                    self.instance['project_id'],
                ],
                capture=True,
            )
            self.last_output = merge_output(result)
            self.last_return_code = result.returncode

            if not result.returncode:
                return True
