from types import EllipsisType
from typing import Iterator, Protocol, TypeVar, overload

P = TypeVar("P", covariant=True)

class IndexableFile(Protocol[P]):  # type: ignore
    @overload
    def __getitem__(self, idx: int) -> P: ...
    @overload
    def __getitem__(self, idx: slice) -> Iterator[P]: ...
    @overload
    def __getitem__(self, idx: EllipsisType) -> Iterator[P]: ...
