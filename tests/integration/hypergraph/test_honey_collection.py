from tests.fixtures.get_project import ProjectGetter
from tests.projects.project_1.src.key_val_collection import KeyValCollection


def test_honey_collection(project: ProjectGetter) -> None:
    location = project("project_1", copy=False) / "collection_1"
    collection = KeyValCollection(location=location, load=True)

    assert collection.loaded

    children = collection.children

    assert {
        (file.location.name, key, value)
        for file in children
        for key, value in {point.value for point in file.children}
    } == {
        ("1_2.csv", "d", 10),
        ("1_2.csv", "b", 4),
        ("1_1.csv", "c", 13),
        ("1_1.csv", "d", 4),
        ("1_2.csv", "a", 2),
        ("1_2.csv", "c", 9),
        ("1_1.csv", "a", 1),
        ("1_1.csv", "b", 3),
    }
