from uuid import UUID

from honeypy.data_graph.meta.node_type import NodeType
from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter


def test_data_graph_initialization(plugin: PluginGetter, context: ContextGetter):
    path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=path / ".honeypy")
    data_graph = ctx.data_graph
    root_uuid = data_graph._root

    root_node = data_graph[root_uuid]
    assert root_node
    assert root_node.node_type == NodeType.ROOT

    project_node = next(
        (
            c
            for c in data_graph.children_of(root_node)
            if c.uuid == UUID("3477c05b-378a-4263-a019-090a80e24add")
        ),
        None,
    )
    assert project_node is not None
    assert project_node.node_type == NodeType.PROJECT

    collection = next(
        (
            c
            for c in data_graph.children_of(project_node)
            if c.uuid == UUID("9908789b-b4bf-42a8-adff-e74d1b455af7")
        ),
        None,
    )
    assert collection is not None
    assert collection.node_type == NodeType.COLLECTION
    assert all(c in collection.raw_metadata for c in ["class_uuid", "data"])

    file = next(
        (
            c
            for c in data_graph.children_of(collection)
            if c.uuid == UUID("1d413ff9-1ce1-443a-ba5b-c5e8f878253c")
        ),
        None,
    )
    assert file is not None
    assert file.raw_metadata == {
        "class_uuid": "1d413ff9-1ce1-443a-ba5b-c5e8f878253c",
        "node_type": "file",
        "data": {"filename": "4_1.csv"},
    }
