from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_file import KeyIntFile


def test_honey_file_gets_data(plugin: PluginGetter):
    path = plugin("plugin_1", copy=False) / "project" / "collection_1" / "1_1.csv"
    file = KeyIntFile(location=path, load=True)

    assert {s.value for s in file} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}


def test_honey_file_load_unload(plugin: PluginGetter):
    path = plugin("plugin_1", copy=False) / "project" / "collection_1" / "1_1.csv"
    file = KeyIntFile(location=path, load=True)

    assert file.loaded

    file.unload()

    assert not file.loaded
