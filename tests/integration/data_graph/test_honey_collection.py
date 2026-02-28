from uuid import UUID

from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter


def test_honey_collection_gets_data(plugin: PluginGetter, context: ContextGetter):
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(plugin_path / ".honeypy")

    collection = ctx.node_factory.create_node(
        UUID("1c829434-9f9e-4f2d-ba7d-e20f4400b7bb")
    )

    assert {
        (file.location.name, key, value) for file in collection for key, value in file
    } == {
        ("1_1.csv", "a", 1),
        ("1_1.csv", "b", 3),
        ("1_1.csv", "c", 9),
        ("1_1.csv", "d", 4),
        ("1_2.csv", "a", 2),
        ("1_2.csv", "b", 4),
        ("1_2.csv", "c", 9),
        ("1_2.csv", "d", 8),
    }
