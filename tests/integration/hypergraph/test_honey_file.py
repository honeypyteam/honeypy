from tests.fixtures.get_project import ProjectGetter
from tests.projects.project_1.src.key_val_file import KeyValFile


def test_honey_file_gets_data(project: ProjectGetter) -> None:
    path = project("project_1", copy=False) / "collection_1" / "1_1.csv"
    file = KeyValFile(location=path, load=True)

    assert {s.value for s in file.children} == {("a", 1), ("b", 3), ("d", 4), ("c", 13)}


def test_honey_file_load_unload(project: ProjectGetter) -> None:
    path = project("project_1", copy=False) / "collection_1" / "1_1.csv"
    file = KeyValFile(location=path, load=True)

    assert file.loaded

    file.unload()

    assert not file.loaded
