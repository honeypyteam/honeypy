from abc import ABC
from pathlib import Path
from typing import Any, Generic, Mapping, Tuple, TypeVar, TypeVarTuple, Unpack

from honeypy.metagraph.meta.honey_node import HoneyNode

from .stubs import IndexableNDFile

Ts = TypeVarTuple("Ts")
M = TypeVar("M", bound=Tuple[Mapping[str, Any], ...])
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")

class NDHoneyFile(
    Generic[M, Unpack[Ts]],
    IndexableNDFile[Unpack[Ts]],
    HoneyNode[M],
    ABC,
):
    @staticmethod
    def _locator(parent_location: Path, metadata: M) -> Path: ...
    @staticmethod
    def _serialise_metadata(metadata: M) -> Any: ...
    @staticmethod
    def _parse_metadata(raw_metadata: Any) -> M: ...
    def _save(self, location: Path, metadata: M) -> None: ...
    def _unload(self) -> None: ...
