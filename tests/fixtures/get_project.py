import shutil
from pathlib import Path
from typing import Protocol

import pytest

CURRENT_FILE: Path = Path(__file__)
PROJECT_FOLDER: Path = CURRENT_FILE.parent.parent / "projects"


assert PROJECT_FOLDER.exists()


class ProjectGetter(Protocol):
    def __call__(self, project_name: str, copy: bool = False) -> Path: ...


@pytest.fixture
def project(tmp_path: Path) -> ProjectGetter:
    def get_project(project_name: str, copy: bool = False) -> Path:
        """Return path to test project.

        If copy is True, copy it into a tempdir and return that path."""
        src = PROJECT_FOLDER / project_name
        if not src.exists():
            raise FileNotFoundError(f"project not found: {src}")

        if not copy:
            return src.resolve()

        dest = tmp_path / project_name
        shutil.copytree(src, dest)
        return dest.resolve()

    return get_project
