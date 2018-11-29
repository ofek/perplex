from .utils import exe_exists


class Docker:
    exe_name = 'docker'

    @classmethod
    def is_available(cls):
        return exe_exists(cls.exe_name)
