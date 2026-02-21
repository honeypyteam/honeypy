from uuid import UUID

from honeypy.data_graph.meta.virtual_node import VirtualNode
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_collection import KeyIntCollection


def test_honey_collection_using_metadata(plugin: PluginGetter):
    location = plugin("plugin_1", copy=True) / "project"

    project = VirtualNode(location=location)

    collection = KeyIntCollection(
        project, uuid=UUID("17c5a2df-8ab9-40f3-92d0-a3e6aabb2b98")
    )

    assert {
        (file.location.name, key, value) for file in collection for key, value in file
    } == {
        ("1_1.csv", "a", 11),
        ("1_1.csv", "b", 53),
        ("1_1.csv", "c", 28),
        ("1_1.csv", "d", 54),
        ("1_2.csv", "a", 10),
        ("1_2.csv", "b", 51),
        ("1_2.csv", "c", 20),
        ("1_2.csv", "d", 24),
    }
