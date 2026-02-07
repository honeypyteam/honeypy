from typing import Generic, Tuple, TypeVar

from honeypy.metagraph.honey_point import HoneyPoint

T = TypeVar("T")


class KeyValPoint(HoneyPoint[Tuple[str, T]], Generic[T]):
    pass
