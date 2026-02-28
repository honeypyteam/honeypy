from __future__ import annotations

from types import EllipsisType
from typing import (
    Any,
    Iterator,
    Literal,
    LiteralString,
    Mapping,
    Protocol,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)

from honeypy.data_graph import NDHoneyFile

Ts = TypeVarTuple("Ts")
M = TypeVar("M", bound=Tuple[Mapping[str, Any], ...])
L = TypeVar("L", bound=Tuple[LiteralString, ...])
Zs = TypeVarTuple("Zs")

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")

class IndexableNDFile(Protocol[Unpack[Ts]]):
    @overload
    def __getitem__(self, idx: int) -> Tuple[Unpack[Ts]]: ...
    @overload
    def __getitem__(self, idx: slice) -> Iterator[Tuple[Unpack[Ts]]]: ...
    @overload
    def __getitem__(self, idx: EllipsisType) -> Iterator[Tuple[Unpack[Ts]]]: ...
    @overload
    def __getitem__(self, idx: Tuple[int, slice]) -> Tuple[Unpack[Ts]]: ...
    @overload
    def __getitem__(
        self, idx: Tuple[int, EllipsisType]
    ) -> Iterator[Tuple[Unpack[Ts]]]: ...
    @overload
    def __getitem__(self, idx: Tuple[slice, slice]) -> Iterator[Tuple[Unpack[Ts]]]: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, Unpack[Zs]]", idx: Tuple[int, Literal[0]]
    ) -> A: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, Unpack[Zs]]", idx: Tuple[int, Literal[1]]
    ) -> B: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, C, Unpack[Zs]]", idx: Tuple[int, Literal[2]]
    ) -> C: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, C, D, Unpack[Zs]]", idx: Tuple[int, Literal[3]]
    ) -> D: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, Unpack[Zs]]",
        idx: Tuple[slice | EllipsisType, Literal[0]],
    ) -> Tuple[A, ...]: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, Unpack[Zs]]",
        idx: Tuple[slice | EllipsisType, Literal[1]],
    ) -> Tuple[B, ...]: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, C, Unpack[Zs]]",
        idx: Tuple[slice | EllipsisType, Literal[2]],
    ) -> Tuple[C, ...]: ...
    @overload
    def __getitem__(  # type: ignore
        self: "NDHoneyFile[L, M, A, B, C, D, Unpack[Zs]]",
        idx: Tuple[slice | EllipsisType, Literal[3]],
    ) -> Tuple[D, ...]: ...
