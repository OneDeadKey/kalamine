"""Some util functions for tests."""

import pkgutil
from typing import Dict

import tomli


def get_layout_dict(filename: str) -> Dict:
    """Return the layout directory path."""

    descriptor = pkgutil.get_data(__package__, f"../layouts/{filename}.toml")
    return tomli.loads(descriptor.decode("utf-8"))
