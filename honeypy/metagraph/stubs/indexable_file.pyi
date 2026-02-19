from itertools import islice
from types import EllipsisType
from typing import Protocol, TypeVar, overload

P = TypeVar("P", covariant=True)

class IndexableFile(Protocol[P]):  # type: ignore
    @overload
    def __getitem__(self, idx: int) -> P: ...
    @overload
    def __getitem__(self, idx: slice) -> islice[P]: ...
    @overload
    def __getitem__(self, idx: EllipsisType) -> islice[P]: ...
