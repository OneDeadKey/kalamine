"""Some util functions for tests."""

from pathlib import Path
from typing import Dict

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def get_layout_dict(filename: str) -> Dict:
    """Return the layout directory path."""

    file_path = Path(__file__).parent.parent / f"layouts/{filename}.toml"
    with file_path.open(mode="rb") as file:
        return tomllib.load(file)
