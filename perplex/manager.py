from copy import deepcopy

from .compose import DockerCompose
from .config import get_instance_dir
from .gcloud import GCloud
from .gsutil import GSUtil
from .kubectl import Kubectl


class InstanceManager:
    def __init__(self, config):
        self.default_config = deepcopy(config)
        self.instance_config = self.default_config.pop('instances').pop(config['instance'])
        self.default_config.update(self.instance_config)

        self.local_path = get_instance_dir(self.instance_config['name'])

        self.gcloud = GCloud(self.default_config)
        self.gsutil = GSUtil(self.default_config)
        self.docker_compose = DockerCompose(self.default_config, self.local_path)
        self.kompose = Kubectl(self.local_path)
