import os
import subprocess
import time
from ast import literal_eval
from contextlib import contextmanager
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

import requests

from .constants import NEED_SHELL


def get_docker_hostname():
    return urlparse(os.getenv('DOCKER_HOST', '')).hostname or 'localhost'


def run_command(command, **kwargs):
    kwargs.setdefault('encoding', 'utf-8')

    if kwargs.pop('capture', False):
        kwargs['stdout'] = kwargs['stderr'] = subprocess.PIPE

    return subprocess.run(command, shell=NEED_SHELL, **kwargs)


def merge_output(result):
    return f'{result.stdout or ""}{result.stderr or ""}'


def wait_for_endpoints(endpoints, timeout=2, attempts=60, wait=1):
    for _ in range(attempts):
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=timeout)
                response.raise_for_status()
            except Exception:
                break
        else:
            break

        time.sleep(wait)


def exe_exists(exe):
    return not not which(exe)


def file_exists(f):
    return os.path.isfile(f)


def dir_exists(d):
    return os.path.isdir(d)


def path_exists(p):
    return os.path.exists(p)


def path_join(path, *paths):
    return os.path.join(path, *paths)


def ensure_dir_exists(d):
    if not dir_exists(d):
        os.makedirs(d)


def ensure_parent_dir_exists(path):
    ensure_dir_exists(os.path.dirname(os.path.abspath(path)))


def create_file(fname):
    ensure_parent_dir_exists(fname)
    with open(fname, 'a'):
        os.utime(fname, None)


def read_file(file, encoding='utf-8'):
    with open(file, 'r', encoding=encoding) as f:
        return f.read()


def write_file(file, contents, encoding='utf-8', newline='\n'):
    ensure_parent_dir_exists(file)

    with open(file, 'w', encoding=encoding, newline=newline) as f:
        return f.write(contents)


def ensure_bytes(s):
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    return s


def ensure_unicode(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return s


def resolve_path(path):
    return str(Path(path).resolve())


def basename(path):
    return os.path.basename(os.path.normpath(path))


def get_next(obj):
    return next(iter(obj))


def string_to_toml_type(s):
    if s.isdigit():
        s = int(s)
    elif s == 'true':
        s = True
    elif s == 'false':
        s = False
    elif s.startswith('['):
        s = literal_eval(s)

    return s


class EnvVars(dict):
    def __init__(self, env_vars=None, ignore=None):
        super(EnvVars, self).__init__(os.environ)
        self.old_env = dict(self)

        if env_vars is not None:
            self.update(env_vars)

        if ignore is not None:
            for env_var in ignore:
                self.pop(env_var, None)

    def __enter__(self):
        os.environ.clear()
        os.environ.update(self)

    def __exit__(self, exc_type, exc_value, traceback):
        os.environ.clear()
        os.environ.update(self.old_env)


@contextmanager
def TempDir():
    with TemporaryDirectory() as d:
        yield resolve_path(d)


@contextmanager
def Chdir(d, cwd=None, env_vars=None):
    origin = cwd or os.getcwd()

    try:
        os.chdir(d)
        if env_vars:
            with EnvVars(env_vars):
                yield
        else:
            yield
    finally:
        os.chdir(origin)


@contextmanager
def TempChdir(cwd=None, env_vars=None):
    with TempDir() as d:
        with Chdir(d, cwd=cwd, env_vars=env_vars):
            yield d


@contextmanager
def mock_context_manager(obj=None):
    yield obj
