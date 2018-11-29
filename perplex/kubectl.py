from .utils import exe_exists


class Kubectl:
    exe_name = 'kubectl'
    file_name_deployment = 'deployment.yaml'
    file_name_ingress = 'ingress.yaml'
    file_name_service = 'service.yaml'

    @classmethod
    def is_available(cls):
        return exe_exists(cls.exe_name)
