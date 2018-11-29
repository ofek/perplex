from .config import config_command
from .create import create_command
from .launch import launch_command
from .start import start_command
from .status import status_command
from .stop import stop_command

ALL_COMMANDS = (config_command, create_command, launch_command, start_command, status_command, stop_command)
