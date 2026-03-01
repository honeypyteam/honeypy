from typing import List, Tuple
from uuid import UUID

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

    file_1 = KeyIntFile.from_uuid(
        UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"),
        context=ctx,
    )
    file_2 = KeyStrFile.from_uuid(
        UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"),
        context=ctx,
    )

    def int_map(point: Tuple[str, int]) -> str:
        return point[0]

    def str_map(point: Tuple[str, str]) -> str:
        return point[0]

    file_3 = file_1.pullback(file_2, on=(int_map, str_map))

    assert [
        (*integer_point, *string_point) for (integer_point, string_point) in file_3
    ] == [
        ("a", 1, "a", "one"),
        ("b", 3, "b", "two"),
        ("c", 9, "c", "three"),
        ("d", 4, "d", "four"),
    ]

    metadata = file_3.metadata

    assert metadata == (
        {"filename": "1_1.csv"},
        {"filename": "2_1.csv"},
    )


def test_large_pullback(plugin: PluginGetter, context: ContextGetter) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file_1 = KeyIntFile.from_uuid(
        UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"),
        context=ctx,
    )
    file_2 = KeyStrFile.from_uuid(
        UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"),
        context=ctx,
    )
    file_3 = KeyStrFile.from_uuid(
        UUID("e0cb7e36-adb3-4d71-9d31-77e804a9c5b6"),
        context=ctx,
    )
    file_4 = KeyBoolFile.from_uuid(
        UUID("1d413ff9-1ce1-443a-ba5b-c5e8f878253c"),
        context=ctx,
    )

    file_5 = file_1.pullback(file_2, on=(int_map, str_map))
    file_6 = file_3.pullback(file_4, on=(str_map, bool_map))
    file_7 = file_5.pullback(file_6, on=(int_str_map, str_bool_map))

    assert [p for p in file_7] == [
        (("a", 1), ("a", "one"), ("a", "two"), ("a", True)),
        (("b", 3), ("b", "two"), ("b", "four"), ("b", True)),
        (("c", 9), ("c", "three"), ("c", "nine"), ("c", False)),
        (("d", 4), ("d", "four"), ("d", "eight"), ("d", False)),
    ]

    file_8 = file_7.pullback(file_1, on=(int_str_str_bool_map, int_map))

    assert file_8[0, 0] == ("a", 1)


def test_nd_file_pullback_predicate(
    plugin: PluginGetter, context: ContextGetter
) -> None:
    plugin_path = plugin("plugin_1", copy=True)
    ctx = context(root_meta_folder=plugin_path / ".honeypy")

    file_1 = KeyIntFile.from_uuid(
        UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"), context=ctx
    )
    file_2 = KeyStrFile.from_uuid(
        UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"),
        context=ctx,
    )

    def predicate(int_point: Tuple[str, int], str_point: Tuple[str, str]) -> bool:
        return int_point[0] == str_point[0]

    file_3 = file_1.pullback(file_2, on=predicate)

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

    file_1 = KeyIntFile.from_uuid(
        uuid=UUID("cbae2d2e-4cfb-4bbf-8df7-f9ab971640c4"), context=ctx
    )
    file_2 = KeyStrFile.from_uuid(
        uuid=UUID("96da523b-7408-49ba-9c6f-2f4c65d924e8"), context=ctx
    )
    file_3 = KeyBoolFile.from_uuid(
        uuid=UUID("1d413ff9-1ce1-443a-ba5b-c5e8f878253c"), context=ctx
    )

    file_4 = file_1.pullback(file_2, on=(int_map, str_map))
    file_5 = file_4.pullback(file_3, on=(int_str_map, bool_map))

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

    # TODO: fix lack of type inference here
    assert list(file_5[:3, 0]) == [("a", 1), ("b", 3), ("c", 9)]  # type: ignore
    assert list(file_5[:3, :1]) == [  # type: ignore
        (("a", 1),),
        (("b", 3),),
        (("c", 9),),
    ]
