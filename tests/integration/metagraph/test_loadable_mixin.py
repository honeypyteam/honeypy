from honeypy.metagraph.meta.virtual_node import VirtualNode
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.array_file import ArrayFile


def test_honey_file_as_adapter(plugin: PluginGetter):
    location = plugin("plugin_1", copy=True) / "project" / "collection_3"

    collection = VirtualNode(location=location)

    file = ArrayFile(
        collection,
        metadata={
            "filename": "3_1.csv",
        },
        load=True,
    )

    with file.data() as data:
        # Check data is there
        assert data.contents == [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

        # Change data the way you would normally work with this object
        # e.g., an np.ndarray or pd.DataFrame
        data.contents = [(4, 5, 6), (7, 8, 9), (10, 11, 12)]

    # Exiting converts the data back into honeypy format

    assert [c.first for c in file] == [4, 7, 10]
