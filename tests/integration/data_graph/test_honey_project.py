from typing import TypeGuard
from uuid import UUID

from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_collection import (
    KeyIntCollection,
)
from tests.plugins.plugin_1.src.key_val_project import KeyVarCollections


def is_key_int_collection(col: KeyVarCollections) -> TypeGuard[KeyIntCollection]:
    return col.metadata.get("title") == "collection 1"


def test_honey_project_load_using_metadata(
    plugin: PluginGetter, context: ContextGetter
):
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(plugin_path / ".honeypy")
    project = ctx.node_factory.create_node(UUID("3477c05b-378a-4263-a019-090a80e24add"))

    assert {col.metadata["title"] for col in project} == {
        "collection 1",
        "collection 2",
        "collection 3",
        "collection 4",
    }

    collection_1 = next((col for col in project if is_key_int_collection(col)), None)

    assert collection_1 is not None

    files = {f for f in collection_1}

    assert {f.metadata["filename"] for f in files} == {"1_1.csv", "1_2.csv"}

    file_1 = next(f for f in files if f.metadata["filename"] == "1_1.csv")

    assert {p for p in file_1} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}
