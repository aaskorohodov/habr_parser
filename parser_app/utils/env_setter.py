"""Setter for environmental variables"""


import io
import os

from pathlib import Path


class EnvSetter:
    """Setter for environmental variables"""

    @staticmethod
    def set_envs(path: str) -> None:
        """Sets environmental variables from the provided path to .env file

        Args:
            path: Path to a .env file"""

        env_file_path = Path(path)

        # Read the .env file and set the environmental variables
        with open(env_file_path, 'r') as file:
            variables = EnvSetter._get_vars(file)

        EnvSetter._set_envs(variables)

    @staticmethod
    def _get_vars(file: io) -> dict[str, str]:
        """Reads variables from a given file and stores them into dict.

        Can clean given file from comments and empty lines. Comments should start with '#' — such lines will be skipped.
        Empty line will also be skipped (empty lines are lines with 'line breaker' only).

        Args:
            file: file, opened with standard 'open()'
        Returns:
            dict, made from given file"""

        variables = {}

        for line in file:
            if line != '\n' and not line.startswith('#'):
                name, value = line.strip().split('=')
                variables[name] = value.strip("'")

        return variables

    @staticmethod
    def _set_envs(variables: dict[str, str]) -> None:
        """Sets content of a given dict as environmental variables

        Args:
            variables: dict, in form [var_name: var_value]"""

        for key, value in variables.items():
            os.environ[key] = value


