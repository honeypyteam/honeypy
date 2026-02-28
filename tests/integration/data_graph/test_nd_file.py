from typing import List, Tuple
from uuid import UUID

from honeypy.transform.pullback import Pullback
from tests.fixtures.get_context import ContextGetter
from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_file import KeyBoolFile, KeyIntFile, KeyStrFile


def int_map(point: Tuple[str, int]) -> str:
    return point[0]


def str_map(point: Tuple[str, str]) -> str:
    return point[0]


def bool_map(point: Tuple[str, bool]) -> str:
    return point[0]


def int_str_map(point: Tuple[Tuple[str, int], Tuple[str, str]]) -> str:
    return point[0][0]


def str_bool_map(point: Tuple[Tuple[str, str], Tuple[str, bool]]) -> str:
    return point[0][0]


def int_str_str_bool_map(
    point: Tuple[Tuple[str, int], Tuple[str, str], Tuple[str, str], Tuple[str, bool]],
) -> str:
    return point[0][0]


def test_nd_file_pullback_projections(
    plugin: PluginGetter, context: ContextGetter
) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file_1 = KeyIntFile(
        uuid=UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"),
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
    )
    file_2 = KeyStrFile(
        uuid=UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"),
        node_factory=ctx.node_factory,
        metadata={"filename": "2_1.csv"},
    )

    def int_map(point: Tuple[str, int]) -> str:
        return point[0]

    def str_map(point: Tuple[str, str]) -> str:
        return point[0]

    pullback = Pullback(ctx)

    file_3 = pullback(file_1, file_2, int_map, str_map)

    assert {
        (*integer_point, *string_point) for (integer_point, string_point) in file_3
    } == {
        ("a", 1, "a", "one"),
        ("b", 3, "b", "two"),
        ("c", 9, "c", "three"),
        ("d", 4, "d", "four"),
    }

    metadata = file_3.metadata

    assert metadata == (
        {"filename": "1_1.csv"},
        {"filename": "2_1.csv"},
    )


def test_large_pullback(plugin: PluginGetter, context: ContextGetter) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file_1 = KeyIntFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
        principal_parent=UUID("1c829434-9f9e-4f2d-ba7d-e20f4400b7bb"),
    )
    file_2 = KeyStrFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "2_1.csv"},
        principal_parent=UUID("17c5a2df-8ab9-40f3-92d0-a3e6aabb2b98"),
    )
    file_3 = KeyStrFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "2_2.csv"},
        principal_parent=UUID("17c5a2df-8ab9-40f3-92d0-a3e6aabb2b98"),
    )
    file_4 = KeyBoolFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "4_1.csv"},
        principal_parent=UUID("9908789b-b4bf-42a8-adff-e74d1b455af7"),
    )

    pullback = Pullback(ctx)

    file_5 = pullback(file_1, file_2, int_map, str_map)
    file_6 = pullback(file_3, file_4, str_map, bool_map)
    file_7 = pullback(file_5, file_6, int_str_map, str_bool_map)

    assert [p for p in file_7] == [
        (("a", 1), ("a", "one"), ("a", "two"), ("a", True)),
        (("b", 3), ("b", "two"), ("b", "four"), ("b", True)),
        (("c", 9), ("c", "three"), ("c", "nine"), ("c", False)),
        (("d", 4), ("d", "four"), ("d", "eight"), ("d", False)),
    ]

    file_8 = pullback(file_1, file_7, int_map, int_str_str_bool_map)

    assert file_8[0, 0] == ("a", 1)


def test_nd_file_pullback_predicate(
    plugin: PluginGetter, context: ContextGetter
) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file_1 = KeyIntFile(
        UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"),
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
    )
    file_2 = KeyStrFile(
        UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"),
        node_factory=ctx.node_factory,
        metadata={"filename": "2_1.csv"},
    )

    def predicate(int_point: Tuple[str, int], str_point: Tuple[str, str]) -> bool:
        return int_point[0] == str_point[0]

    pullback = Pullback(ctx)

    file_3 = pullback(file_1, file_2, predicate)

    assert {
        (*integer_point, *string_point) for (integer_point, string_point) in file_3
    } == {
        ("a", 1, "a", "one"),
        ("b", 3, "b", "two"),
        ("c", 9, "c", "three"),
        ("d", 4, "d", "four"),
    }


def test_nd_file_slicing(plugin: PluginGetter, context: ContextGetter) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(plugin_path / ".honeypy")

    file_1 = KeyIntFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "1_1.csv"},
        principal_parent=UUID("1c829434-9f9e-4f2d-ba7d-e20f4400b7bb"),
    )
    file_2 = KeyStrFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "2_1.csv"},
        principal_parent=UUID("17c5a2df-8ab9-40f3-92d0-a3e6aabb2b98"),
    )
    file_3 = KeyBoolFile(
        node_factory=ctx.node_factory,
        metadata={"filename": "4_1.csv"},
        principal_parent=UUID("9908789b-b4bf-42a8-adff-e74d1b455af7"),
    )

    pullback = Pullback(ctx)

    file_4 = pullback(file_1, file_2, int_map, str_map)
    file_5 = pullback(file_4, file_3, int_str_map, bool_map)

    all_points: List[Tuple[Tuple[str, int], Tuple[str, str], Tuple[str, bool]]] = [
        (("a", 1), ("a", "one"), ("a", True)),
        (("b", 3), ("b", "two"), ("b", True)),
        (("c", 9), ("c", "three"), ("c", False)),
        (("d", 4), ("d", "four"), ("d", False)),
    ]

    assert list(file_5) == all_points

    # TODO: such projections really are transformations on the files. They should
    # be coded such that the file sees a projection in its provenance
    assert file_5[2] == (("c", 9), ("c", "three"), ("c", False))
    assert file_5[2, 0] == ("c", 9)

    assert list(file_5[:3, 0]) == [("a", 1), ("b", 3), ("c", 9)]
    assert list(file_5[:3, :1]) == [(("a", 1),), (("b", 3),), (("c", 9),)]
