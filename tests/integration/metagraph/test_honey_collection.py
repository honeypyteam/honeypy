from datetime import datetime, timezone

from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_collection import KeyIntCollection


def test_honey_collection(plugin: PluginGetter):
    location = plugin("plugin_1", copy=False) / "project" / "collection_1"
    collection = KeyIntCollection(location=location, load=True)

    assert collection.loaded

    assert {
        (file.location.name, key, value)
        for file in collection
        for key, value in {point.value for point in file}
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

    assert collection.metadata == {
        "title": "collection 1",
        "description": "collection of key value files in the 1-10 range",
        "created_at": datetime(2026, 3, 4, 12, 0, tzinfo=timezone.utc),
        "created_by": "test user 1",
    }
