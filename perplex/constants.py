CONTAINER_NAME = 'pms'
LATEST_IMAGE = 'ofekmeister/perplex:0.0.1'
SERVICE_ACCOUNT_STORAGE_KEY_FILE = 'credentials.json'


class ShellDetector:
    def __init__(self):
        self.val = None

    def __bool__(self):
        # https://github.com/python/cpython/blob/cba16b748c286261b5bc45e6ff3c26aea2373f43/Lib/subprocess.py#L1163
        # https://github.com/python/cpython/blob/cba16b748c286261b5bc45e6ff3c26aea2373f43/Lib/subprocess.py#L1397
        if self.val is None:
            import platform

            self.val = platform.system() == 'Windows'

        return self.val


# After 9 years, I finally know why subprocess on Windows occasionally needs `shell=True` :facepalm:
# https://stackoverflow.com/questions/4965175/make-subprocess-find-git-executable-on-windows/10555130#10555130
# https://bugs.python.org/issue8557
NEED_SHELL = ShellDetector()
