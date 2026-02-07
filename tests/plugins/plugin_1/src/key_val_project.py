from typing import Dict, Iterable, TypeAlias

from honeypy.metagraph.honey_project import HoneyProject
from tests.plugins.plugin_1.src.key_val_collection import (
    KeyIntCollection,
    KeyStrCollection,
)

KeyVarCollections: TypeAlias = KeyIntCollection | KeyStrCollection


class KeyValProject(HoneyProject[KeyVarCollections]):
    def _load(self) -> Iterable[KeyVarCollections]:
        # TODO: see how we can use metadata to choose class
        # dynamically
        for name in ("collection_1", "collection_2"):
            path = self._location / name

            if name == "collection_1":
                yield KeyIntCollection(location=path, principal_parent=self, load=True)
            elif name == "collection_2":
                yield KeyStrCollection(location=path, principal_parent=self, load=True)

    def _unload(self) -> None:
        for child in self._children:
            child.unload()

    def _load_metadata(self) -> Dict:
        return {}
