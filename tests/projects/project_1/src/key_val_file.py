from typing import Iterable, List, Set, TypedDict

from honeypy.metagraph.honey_file import HoneyFile
from honeypy.metagraph.honey_point import HoneyPoint
from tests.projects.project_1.src.str_int_point import StrIntTuple


class Metadata(TypedDict):
    columns: List[str]


class KeyValFile(HoneyFile[StrIntTuple]):
    def _load(self) -> Iterable[HoneyPoint[StrIntTuple]]:
        pts: Set[HoneyPoint[StrIntTuple]] = set()

        with self._location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.add(HoneyPoint[StrIntTuple]((key, int(val)), parents={self}))

        return pts

    def _load_metadata(self) -> Metadata:
        with self._location.open("r", encoding="utf-8") as fh:
            line = next(fh)
            cols = line.split(",")

            return {"columns": cols}

    def _unload(self) -> None:
        return
