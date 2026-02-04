from typing import Tuple, TypeAlias

from honeypy.metagraph.honey_point import HoneyPoint

StrIntTuple: TypeAlias = Tuple[str, int]
StrIntPoint = HoneyPoint[StrIntTuple]
