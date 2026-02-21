from honeypy.metagraph.meta.virtual_node import VirtualNode
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_file import KeyIntFile


def test_honey_file_gets_data(plugin: PluginGetter):
    location = plugin("plugin_1", copy=True) / "project" / "collection_1"

    collection = VirtualNode(location=location)

    file = KeyIntFile(principal_parent=collection, metadata={"filename": "1_1.csv"})

    assert {s for s in file} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}


def test_honey_file_slicing(plugin: PluginGetter):
    location = plugin("plugin_1", copy=True) / "project" / "collection_1"
    collection = VirtualNode(location=location)

    file = KeyIntFile(principal_parent=collection, metadata={"filename": "1_1.csv"})

    assert file[0] == ("a", 1)
    assert file[-1] == ("d", 4)
    assert list(file[1:3]) == [("b", 3), ("c", 9)]
    assert list(file[:3]) == [("a", 1), ("b", 3), ("c", 9)]
