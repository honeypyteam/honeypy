from typing import List, Set, TypedDict

from honeypy.metagraph.honey_file import HoneyFile
from tests.projects.project_1.src.str_int_point import StrIntPoint


class Metadata(TypedDict):
    columns: List[str]


class KeyValFile(HoneyFile[StrIntPoint]):
    def _load(self):
        pts: Set[StrIntPoint] = set()

        with self._location.open("r", encoding="utf-8") as fh:
            next(fh)

            for line in fh:
                key, val = line.split(",")
                pts.add(StrIntPoint((key, int(val)), parents={self}))

        return pts

    def _load_metadata(self) -> Metadata:
        with self._location.open("r", encoding="utf-8") as fh:
            line = next(fh)
            cols = line.split(",")

            return {"columns": cols}

    def _unload(self) -> None:
        return
