from honeypy.bootstrap.bootstrap import _register_node_classes
from tests.fixtures.get_context import context  # noqa: F401
from tests.fixtures.get_plugin import plugin  # noqa: F401
from tests.plugins.plugin_1.src.array_file import ArrayFile
from tests.plugins.plugin_1.src.array_file_collection import ArrayFileCollection
from tests.plugins.plugin_1.src.key_val_collection import (
    KeyBoolCollection,
    KeyIntCollection,
    KeyStrCollection,
)
from tests.plugins.plugin_1.src.key_val_file import (
    KeyBoolFile,
    KeyIntFile,
    KeyStrFile,
)
from tests.plugins.plugin_1.src.key_val_project import KeyValProject  # noqa: F401

_register_node_classes(
    node_classes=[
        ArrayFile,
        KeyStrCollection,
        KeyIntCollection,
        KeyBoolCollection,
        KeyStrFile,
        KeyBoolFile,
        KeyIntFile,
        KeyValProject,
        ArrayFileCollection,
    ]
)
