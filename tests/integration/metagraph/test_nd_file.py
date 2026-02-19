from typing import List, Tuple

from honeypy.metagraph.meta.virtual_node import VirtualNode
from honeypy.transform.pullback import Pullback
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


def test_nd_file_pullback_projections(plugin: PluginGetter) -> None:
    location = plugin("plugin_1", copy=True) / "project" / "collection_1"

    collection = VirtualNode(location)

    file_1 = KeyIntFile(collection, metadata={"filename": "1_1.csv"}, load=True)
    file_2 = KeyStrFile(collection, metadata={"filename": "1_3.csv"}, load=True)

    def int_map(point: Tuple[str, int]) -> str:
        return point[0]

    def str_map(point: Tuple[str, str]) -> str:
        return point[0]

    pullback = Pullback()

    file_3 = pullback(file_1, file_2, int_map, str_map)

    assert {
        (*integer_point, *string_point) for (integer_point, string_point) in file_3
    } == {
        ("a", 1, "a", "one"),
        ("b", 3, "b", "three"),
        ("c", 9, "c", "nine"),
        ("d", 4, "d", "four"),
    }

    metadata = file_3.metadata

    assert metadata == (
        {"filename": "1_1.csv"},
        {"filename": "1_3.csv"},
    )


def test_large_pullback(plugin: PluginGetter) -> None:
    path = plugin("plugin_1", copy=True) / "project"

    collection_1 = VirtualNode(path / "collection_1")
    collection_2 = VirtualNode(path / "collection_2")
    collection_4 = VirtualNode(path / "collection_4")

    file_1 = KeyIntFile(collection_1, metadata={"filename": "1_1.csv"}, load=True)
    file_2 = KeyStrFile(collection_2, metadata={"filename": "1_1.csv"}, load=True)
    file_3 = KeyStrFile(collection_2, metadata={"filename": "1_2.csv"}, load=True)
    file_4 = KeyBoolFile(collection_4, metadata={"filename": "4_1.csv"}, load=True)

    pullback = Pullback()

    file_5 = pullback(file_1, file_2, int_map, str_map)
    file_6 = pullback(file_3, file_4, str_map, bool_map)
    file_7 = pullback(file_5, file_6, int_str_map, str_bool_map)

    assert [p for p in file_7] == [
        (("a", 1), ("a", "11"), ("a", "10"), ("a", True)),
        (("b", 3), ("b", "53"), ("b", "51"), ("b", True)),
        (("c", 9), ("c", "28"), ("c", "20"), ("c", False)),
        (("d", 4), ("d", "54"), ("d", "24"), ("d", False)),
    ]

    file_8 = pullback(file_1, file_7, int_map, int_str_str_bool_map)

    assert file_8[0, 0] == ("a", 1)


def test_nd_file_pullback_predicate(plugin: PluginGetter) -> None:
    location = plugin("plugin_1", copy=True) / "project" / "collection_1"

    collection = VirtualNode(location)

    file_1 = KeyIntFile(collection, metadata={"filename": "1_1.csv"}, load=True)
    file_2 = KeyStrFile(collection, metadata={"filename": "1_3.csv"}, load=True)

    def predicate(int_point: Tuple[str, int], str_point: Tuple[str, str]) -> bool:
        return int_point[0] == str_point[0]

    pullback = Pullback()

    file_3 = pullback(file_1, file_2, predicate)

    assert {
        (*integer_point, *string_point) for (integer_point, string_point) in file_3
    } == {
        ("a", 1, "a", "one"),
        ("b", 3, "b", "three"),
        ("c", 9, "c", "nine"),
        ("d", 4, "d", "four"),
    }


def test_nd_file_slicing(plugin: PluginGetter) -> None:
    plugin_path = plugin("plugin_1", copy=True)

    location_1 = plugin_path / "project" / "collection_1"
    location_2 = plugin_path / "project" / "collection_4"

    collection_1 = VirtualNode(location_1)
    collection_2 = VirtualNode(location_2)

    file_1 = KeyIntFile(collection_1, metadata={"filename": "1_1.csv"}, load=True)
    file_2 = KeyStrFile(collection_1, metadata={"filename": "1_3.csv"}, load=True)
    file_3 = KeyBoolFile(collection_2, metadata={"filename": "4_1.csv"}, load=True)

    pullback = Pullback()

    file_4 = pullback(file_1, file_2, int_map, str_map)
    file_5 = pullback(file_4, file_3, int_str_map, bool_map)

    all_points: List[Tuple[Tuple[str, int], Tuple[str, str], Tuple[str, bool]]] = [
        (("a", 1), ("a", "one"), ("a", True)),
        (("b", 3), ("b", "three"), ("b", True)),
        (("c", 9), ("c", "nine"), ("c", False)),
        (("d", 4), ("d", "four"), ("d", False)),
    ]

    assert list(file_5) == all_points

    # TODO: such projections really are transformations on the files. They should
    # be coded such that the file sees a projection in its provenance
    assert list(file_5[...]) == all_points
    assert file_5[2] == (("c", 9), ("c", "nine"), ("c", False))
    assert file_5[2, 0] == ("c", 9)
    assert file_5[1, :] == (("b", 3), ("b", "three"), ("b", True))

    assert list(file_5[:3, 0]) == [("a", 1), ("b", 3), ("c", 9)]
    assert list(file_5[:3, :1]) == [(("a", 1),), (("b", 3),), (("c", 9),)]
