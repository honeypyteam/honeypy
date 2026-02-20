from typing import (
    Any,
    Callable,
    LiteralString,
    Mapping,
    Tuple,
    TypeVar,
    TypeVarTuple,
    Unpack,
    overload,
)

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.nd_collection import NDHoneyCollection
from honeypy.metagraph.nd_file import NDHoneyFile
from honeypy.transform.meta.honey_transform import HoneyTransform

K = TypeVar("K")

L1 = TypeVar("L1", bound=LiteralString)
L2 = TypeVar("L2", bound=LiteralString)
L3 = TypeVar("L3", bound=LiteralString)
L4 = TypeVar("L4", bound=LiteralString)

Lt = TypeVarTuple("Lt")

P1 = TypeVar("P1", covariant=True)
P2 = TypeVar("P2", covariant=True)
P3 = TypeVar("P3", covariant=True)
P4 = TypeVar("P4", covariant=True)

F1 = TypeVar("F1", bound=HoneyFile, covariant=True)
F2 = TypeVar("F2", bound=HoneyFile, covariant=True)
F3 = TypeVar("F3", bound=HoneyFile, covariant=True)
F4 = TypeVar("F4", bound=HoneyFile, covariant=True)

Ts = TypeVarTuple("Ts")

M1 = TypeVar("M1", bound=Mapping[str, Any])
M2 = TypeVar("M2", bound=Mapping[str, Any])
M3 = TypeVar("M3", bound=Mapping[str, Any])
M4 = TypeVar("M4", bound=Mapping[str, Any])

Mt = TypeVarTuple("Mt")

class Pullback(HoneyTransform):
    # TODO: This could be simplified if Python had multiple variadic argument unpacking
    # for sinks. When this is added sometime in the future, definitely add those
    # signatures, and remove the need for the 2,2, 2,3 etc. checks

    # Some of what I'm doing seems illegal... and mypy isn't happy... But if you ignore
    # it works perfectly fine. See for example `test_nd_file.py`

    # SPECIFIC MULTIPLE VARIADIC ARGUMENTS CASES #
    # ------------------------------------------ #
    # Covers 2xN, 3xN, 4xN, Nx2, Nx3, Nx4

    # Files

    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[L1, L2, Unpack[Lt]], Tuple[M1, M2, Unpack[Mt]], P1, P2, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[Tuple[L1, L2, L3], Tuple[M1, M2, M3], P1, P2, P3],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2, P3]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[L1, L2, L3, Unpack[Lt]], Tuple[M1, M2, M3, Unpack[Mt]], P1, P2, P3, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], P1, P2, P3, P4
        ],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2, P3, P4]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[L1, L2, L3, L4, Unpack[Lt]], Tuple[M1, M2, M3, M4, Unpack[Mt]], P1, P2, P3, P4, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[P1, P2]], K],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2], Tuple[Unpack[Mt], M1, M2], Unpack[Ts], P1, P2]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[Tuple[L1, L2, L3], Tuple[M1, M2, M3], P1, P2, P3],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[P1, P2, P3]], K],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2, L3], Tuple[Unpack[Mt], M1, M2, M3], Unpack[Ts], P1, P2, P3]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], P1, P2, P3, P4
        ],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[P1, P2, P3, P4]], K],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2, L3, L4], Tuple[Unpack[Mt], M1, M2, M3, M4], Unpack[Ts], P1, P2, P3, P4]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyFile[Tuple[L1, L2, Unpack[Lt]], Tuple[M1, M2, Unpack[Mt]], P1, P2, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[Tuple[L1, L2, L3], Tuple[M1, M2, M3], P1, P2, P3],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2, P3], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyFile[Tuple[L1, L2, L3, Unpack[Lt]], Tuple[M1, M2, M3, Unpack[Mt]], P1, P2, P3, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyFile[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], P1, P2, P3, P4
        ],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[P1, P2, P3, P4], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyFile[Tuple[L1, L2, L3, L4, Unpack[Lt]], Tuple[M1, M2, M3, M4, Unpack[Mt]], P1, P2, P3, P4, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[P1, P2]], bool],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2], Tuple[Unpack[Mt], M1, M2], Unpack[Ts], P1, P2]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[Tuple[L1, L2, L3], Tuple[M1, M2, M3], P1, P2, P3],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[P1, P2, P3]], bool],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2, L3], Tuple[Unpack[Mt], M1, M2, M3], Unpack[Ts], P1, P2, P3]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyFile[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], P1, P2, P3, P4
        ],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[P1, P2, P3, P4]], bool],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L1, L2, L3, L4], Tuple[Unpack[Mt], M1, M2, M3, M4], Unpack[Ts], P1, P2, P3, P4]: ...  # type: ignore

    # Collections

    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[Tuple[L1, L2, Unpack[Lt]], Tuple[M1, M2, Unpack[Mt]], F1, F2, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[Tuple[L1, L2, L3], Tuple[M1, M2, M3], F1, F2, F3],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2, F3]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[Tuple[L1, L2, L3, Unpack[Lt]], Tuple[M1, M2, M3, Unpack[Mt]], F1, F2, F3, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], F1, F2, F3, F4
        ],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2, F3, F4]], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[Tuple[L1, L2, L3, L4, Unpack[Lt]], Tuple[M1, M2, M3, M4, Unpack[Mt]], F1, F2, F3, F4, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[F1, F2]], K],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2], Tuple[Unpack[Mt], M1, M2], Unpack[Ts], F1, F2]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[Tuple[L1, L2, L3], Tuple[M1, M2, M3], F1, F2, F3],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[F1, F2, F3]], K],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2, L3], Tuple[Unpack[Mt], M1, M2, M3], Unpack[Ts], F1, F2, F3]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], F1, F2, F3, F4
        ],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[Tuple[F1, F2, F3, F4]], K],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2, L3, L4], Tuple[Unpack[Mt], M1, M2, M3, M4], Unpack[Ts], F1, F2, F3, F4]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyCollection[Tuple[L1, L2, Unpack[Lt]], Tuple[M1, M2, Unpack[Mt]], F1, F2, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[Tuple[L1, L2, L3], Tuple[M1, M2, M3], F1, F2, F3],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2, F3], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyCollection[Tuple[L1, L2, L3, Unpack[Lt]], Tuple[M1, M2, M3, Unpack[Mt]], F1, F2, F3, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(  # type: ignore
        self,
        node_1: NDHoneyCollection[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], F1, F2, F3, F4
        ],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[Tuple[F1, F2, F3, F4], Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyCollection[Tuple[L1, L2, L3, L4, Unpack[Lt]], Tuple[M1, M2, M3, M4, Unpack[Mt]], F1, F2, F3, F4, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[F1, F2]], bool],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2], Tuple[Unpack[Mt], M1, M2], Unpack[Ts], F1, F2]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[Tuple[L1, L2, L3], Tuple[M1, M2, M3], F1, F2, F3],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[F1, F2, F3]], bool],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2, L3], Tuple[Unpack[Mt], M1, M2, M3], Unpack[Ts], F1, F2, F3]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: NDHoneyCollection[
            Tuple[L1, L2, L3, L4], Tuple[M1, M2, M3, M4], F1, F2, F3, F4
        ],
        map_1: Callable[[Tuple[Unpack[Ts]], Tuple[F1, F2, F3, F4]], bool],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L1, L2, L3, L4], Tuple[Unpack[Mt], M1, M2, M3, M4], Unpack[Ts], F1, F2, F3, F4]: ...  # type: ignore

    # GENERAL CASE WITH 1 VARIADIC TYPEVAR #
    # ------------------------------------ #

    @overload
    def __call__(
        self,
        node_1: HoneyFile[L1, M1, P1],
        node_2: HoneyFile[L2, M2, P2],
        map_1: Callable[[P1], K],
        map_2: Callable[[P2], K],
    ) -> NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2]: ...
    @overload
    def __call__(
        self,
        node_1: HoneyFile[L1, M1, P1],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[P1], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyFile[Tuple[L1, Unpack[Lt]], Tuple[M1, Unpack[Mt]], P1, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyFile[L2, M2, P2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[P2], K],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L2], Tuple[Unpack[Mt], M2], Unpack[Ts], P2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyFile[L1, M1, P1],
        node_2: HoneyFile[L2, M2, P2],
        map_1: Callable[[P1, P2], bool],
    ) -> NDHoneyFile[Tuple[L1, L2], Tuple[M1, M2], P1, P2]: ...
    @overload
    def __call__(
        self,
        node_1: HoneyFile[L1, M1, P1],
        node_2: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[P1, Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyFile[Tuple[L1, Unpack[Lt]], Tuple[M1, Unpack[Mt]], P1, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyFile[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyFile[L2, M2, P2],
        map_1: Callable[[Tuple[Unpack[Ts]], P2], bool],
    ) -> NDHoneyFile[Tuple[Unpack[Lt], L2], Tuple[Unpack[Mt], M2], Unpack[Ts], P2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[L1, M1, F1],
        node_2: HoneyCollection[L2, M2, F2],
        map_1: Callable[[F1], K],
        map_2: Callable[[F2], K],
    ) -> NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2]: ...
    @overload
    def __call__(
        self,
        node_1: HoneyCollection[L1, M1, F1],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[F1], K],
        map_2: Callable[[Tuple[Unpack[Ts]]], K],
    ) -> NDHoneyCollection[Tuple[L1, Unpack[Lt]], Tuple[M1, Unpack[Mt]], F1, Unpack[Ts]]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyCollection[L2, M2, F2],
        map_1: Callable[[Tuple[Unpack[Ts]]], K],
        map_2: Callable[[F2], K],
    ) -> NDHoneyCollection[Tuple[Unpack[Lt], L2], Tuple[Unpack[Mt], M2], Unpack[Ts], F2]: ...  # type: ignore

    # Wait for multiple variadic argument unpacking for an extra signature

    @overload
    def __call__(
        self,
        node_1: HoneyCollection[L1, M1, F1],
        node_2: HoneyCollection[L2, M2, F2],
        map_1: Callable[[F1, F2], bool],
    ) -> NDHoneyCollection[Tuple[L1, L2], Tuple[M1, M2], F1, F2]: ...
    @overload
    def __call__(
        self,
        node_1: HoneyCollection[L1, M1, F1],
        node_2: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        map_1: Callable[[F1, Tuple[Unpack[Ts]]], bool],
    ) -> NDHoneyCollection[  # type: ignore
        Tuple[L1, Unpack[Lt]],  # type: ignore
        Tuple[M1, Unpack[Mt]],  # type: ignore
        F1,
        Unpack[Ts],
    ]: ...  # type: ignore
    @overload
    def __call__(
        self,
        node_1: NDHoneyCollection[Tuple[Unpack[Lt]], Tuple[Unpack[Mt]], Unpack[Ts]],  # type: ignore
        node_2: HoneyCollection[L2, M2, F2],
        map_1: Callable[[Tuple[Unpack[Ts]], F2], bool],
    ) -> NDHoneyCollection[  # type: ignore
        Tuple[Unpack[Lt], L2],  # type: ignore
        Tuple[Unpack[Mt], M2],  # type: ignore
        Unpack[Ts],
        F2,
    ]: ...
