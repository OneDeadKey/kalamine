"""Some util functions for tests."""

from pathlib import Path
from typing import Dict, Optional

import tomli


def get_layout_dict(
    filename: str, extraMapping: Optional[Dict[str, Dict[str, str]]] = None
) -> Dict:
    """Return the layout directory path."""

    file_path = Path(__file__).parent.parent / f"layouts/{filename}.toml"
    with file_path.open(mode="rb") as file:
        layout = tomli.load(file)
        if extraMapping:
            layout.update({"mapping": extraMapping})
        return layout
