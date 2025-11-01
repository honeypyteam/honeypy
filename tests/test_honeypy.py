from test_plugins.minimal_plugin import MinimalPlugin


def test_honeypy():
    honeypy = MinimalPlugin()

    assert honeypy is not None
