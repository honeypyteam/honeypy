from tests.fixtures.get_project import ProjectGetter
from tests.projects.project_1.src.key_val_file import KeyIntFile, KeyStrFile
from tests.projects.project_1.src.key_val_point import KeyValPoint


def test_nd_file_pullback(project: ProjectGetter) -> None:
    location = project("project_1", copy=False) / "collection_1"

    file_1 = KeyIntFile(location=location / "1_1.csv", load=True)
    file_2 = KeyStrFile(location=location / "1_3.csv", load=True)

    def int_map(point: KeyValPoint[int]) -> str:
        return point.value[0]

    def str_map(point: KeyValPoint[str]) -> str:
        return point.value[0]

    file_3 = file_1.pullback(file_2, int_map, str_map)

    children = file_3.children

    assert {(*integer.value, *string.value) for (integer, string) in children} == {
        ("a", 1, "a", "one\n"),
        ("b", 3, "b", "three\n"),
        ("c", 9, "c", "nine\n"),
        ("d", 4, "d", "four"),
    }
