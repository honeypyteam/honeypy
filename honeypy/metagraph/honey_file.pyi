from abc import ABC
from pathlib import Path
from typing import Any, Generic, Mapping, TypeVar

from honeypy.metagraph.meta.honey_node import HoneyNode
from honeypy.metagraph.stubs.indexable_file import IndexableFile

P = TypeVar("P", covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])

class HoneyFile(Generic[M, P], IndexableFile[P], HoneyNode[M], ABC):
    @staticmethod
    def _locator(parent_location: Path, metadata: M) -> Path: ...
    @staticmethod
    def _serialise_metadata(metadata: M) -> Any: ...
    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> M: ...
    def _save(self, location: Path, metadata: M) -> None: ...
    def _unload(self) -> None: ...
