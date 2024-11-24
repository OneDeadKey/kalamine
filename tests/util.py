"""Some util functions for tests."""

from pathlib import Path
from typing import Dict

import tomli


def get_layout_dict(filename: str) -> Dict:
    """Return the layout directory path."""

    file_path = Path(__file__).parent.parent / f"layouts/{filename}.toml"
    with file_path.open(mode="rb") as file:
        return tomli.load(file)
