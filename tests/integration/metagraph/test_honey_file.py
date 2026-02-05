from tests.fixtures.get_project import ProjectGetter
from tests.projects.project_1.src.key_val_file import KeyIntFile


def test_honey_file_gets_data(project: ProjectGetter) -> None:
    path = project("project_1", copy=False) / "collection_1" / "1_1.csv"
    file = KeyIntFile(location=path, load=True)

    assert {s.value for s in file} == {("a", 1), ("b", 3), ("c", 9), ("d", 4)}


def test_honey_file_load_unload(project: ProjectGetter) -> None:
    path = project("project_1", copy=False) / "collection_1" / "1_1.csv"
    file = KeyIntFile(location=path, load=True)

    assert file.loaded

    file.unload()

    assert not file.loaded
