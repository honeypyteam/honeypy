import shutil
from pathlib import Path
from typing import Protocol

import pytest

CURRENT_FILE: Path = Path(__file__)
PLUGINS_FOLDER: Path = CURRENT_FILE.parent.parent / "plugins"


assert PLUGINS_FOLDER.exists()


class PluginGetter(Protocol):
    def __call__(self, plugin_name: str, copy: bool = False) -> Path: ...


@pytest.fixture
def plugin(tmp_path: Path) -> PluginGetter:
    def get_plugin(plugin_name: str, copy: bool = False) -> Path:
        """Return path to test plugin.

        If copy is True, copy it into a tempdir and return that path."""
        src = PLUGINS_FOLDER / plugin_name
        if not src.exists():
            raise FileNotFoundError(f"plugin not found: {src}")

        if not copy:
            return src.resolve()

        dest = tmp_path / plugin_name
        shutil.copytree(src, dest)
        return dest.resolve()

    return get_plugin
