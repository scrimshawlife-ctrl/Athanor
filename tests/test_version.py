from athanor import __version__


def test_version_present():
    assert __version__
    assert __version__[0].isdigit()
