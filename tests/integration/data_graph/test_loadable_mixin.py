from uuid import UUID

from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.array_file import ArrayFile


def test_honey_file_as_adapter(plugin: PluginGetter, context: ContextGetter):
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file = ArrayFile(
        node_factory=ctx.node_factory,
        principal_parent=UUID("8e4d7b9e-f3b4-4f69-9ae4-83061637ace0"),
        metadata={
            "filename": "3_1.csv",
        },
    )

    with file.data() as data:
        # Check data is there
        assert data.contents == [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

        # Change data the way you would normally work with this object
        # e.g., an np.ndarray or pd.DataFrame
        data.contents = [(4, 5, 6), (7, 8, 9), (10, 11, 12)]

    # Exiting converts the data back into honeypy format

    assert [c.first for c in file] == [4, 7, 10]
