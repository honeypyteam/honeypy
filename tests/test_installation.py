import subprocess


def test_package_installation():
    result = subprocess.run(
        ["pip", "show", "honeypy", "--no-cache-dir"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "honeypy" in result.stdout
