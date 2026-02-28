from pathlib import Path
from typing import Protocol

import pytest

from honeypy.bootstrap.bootstrap import _get_context
from honeypy.services.context import HoneyContext


class ContextGetter(Protocol):
    def __call__(self, root_meta_folder: Path) -> HoneyContext: ...


@pytest.fixture
def context() -> ContextGetter:
    def get_context(root_meta_folder: Path) -> HoneyContext:
        return _get_context(root_meta_folder)

    return get_context
