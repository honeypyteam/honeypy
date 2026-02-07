from tests.fixtures.get_plugin import PluginGetter
from tests.plugins.plugin_1.src.key_val_file import KeyIntFile, KeyStrFile
from tests.plugins.plugin_1.src.key_val_point import KeyValPoint


def test_nd_file_pullback(plugin: PluginGetter) -> None:
    location = plugin("plugin_1", copy=False) / "project" / "collection_1"

    file_1 = KeyIntFile(location=location / "1_1.csv", load=True)
    file_2 = KeyStrFile(location=location / "1_3.csv", load=True)

    def int_map(point: KeyValPoint[int]) -> str:
        return point.value[0]

    def str_map(point: KeyValPoint[str]) -> str:
        return point.value[0]

    file_3 = file_1.pullback(file_2, int_map, str_map)

    assert {
        (*integer_point.value, *string_point.value)
        for (integer_point, string_point) in file_3
    } == {
        ("a", 1, "a", "one\n"),
        ("b", 3, "b", "three\n"),
        ("c", 9, "c", "nine\n"),
        ("d", 4, "d", "four"),
    }
