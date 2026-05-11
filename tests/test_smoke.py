def test_package_importable():
    import sc_companion
    assert sc_companion.__version__ == "0.1.0"
