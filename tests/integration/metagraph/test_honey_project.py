from typing import TypeGuard

from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_collection import (
    KeyIntCollection,
)
from tests.plugins.plugin_1.src.key_val_project import KeyValProject, KeyVarCollections


def is_key_int_collection(col: KeyVarCollections) -> TypeGuard[KeyIntCollection]:
    # TODO: well, title is probably not the best test
    # for this. Probably want to add better metadata for
    # to encapsulate what kind of collection it is
    return col.metadata.get("title") == "collection 1"


def test_honey_project_load(plugin: PluginGetter):
    path = plugin("plugin_1", copy=False) / "project"

    project = KeyValProject(location=path, load=True)

    project.load()

    assert {col.metadata["title"] for col in project} == {
        "collection 1",
        "collection 2",
    }

    collection_1 = next((col for col in project if is_key_int_collection(col)), None)

    assert collection_1 is not None

    files = {f for f in collection_1}

    assert {f.metadata["filename"] for f in files} == {"1_1.csv", "1_2.csv", "1_3.csv"}

    file_1 = next(f for f in files if f.metadata["filename"] == "1_1.csv")

    assert {p.value for p in file_1} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}
