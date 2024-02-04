"""Some util functions for tests."""

from pathlib import Path


def get_layout_path() -> Path:
    """Return the layout directory path."""
    return Path(__file__).parent.parent / "layouts"
