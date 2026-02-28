from abc import ABC
from pathlib import Path
from typing import Any, Generic, Iterator, LiteralString, Mapping, TypeVar

from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.data_graph.stubs.indexable_file import IndexableFile

P_co = TypeVar("P_co", covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])
L = TypeVar("L", bound=LiteralString)

class HoneyFile(Generic[L, M, P_co], IndexableFile[P_co], HoneyNode[L, M, P_co], ABC):
    @staticmethod
    def _locator(parent_location: Path, metadata: M) -> Path: ...
    @staticmethod
    def _serialise_metadata(metadata: M) -> Any: ...
    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> M: ...
    def __iter__(self) -> Iterator[P_co]: ...
