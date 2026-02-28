from uuid import UUID

from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_file import KeyIntFile


def test_honey_file_gets_data(plugin: PluginGetter, context: ContextGetter):
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file = KeyIntFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
        principal_parent=UUID("1c829434-9f9e-4f2d-ba7d-e20f4400b7bb"),
    )

    assert {s for s in file} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}


def test_honey_file_slicing(plugin: PluginGetter, context: ContextGetter):
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file = KeyIntFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
        principal_parent=UUID("1c829434-9f9e-4f2d-ba7d-e20f4400b7bb"),
    )

    assert file[0] == ("a", 1)
    assert file[-1] == ("d", 4)
    assert list(file[1:3]) == [("b", 3), ("c", 9)]
    assert list(file[:3]) == [("a", 1), ("b", 3), ("c", 9)]
