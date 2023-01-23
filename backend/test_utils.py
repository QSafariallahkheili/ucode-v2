from utils import sure_float


def test_sure_float_from_float():
    assert sure_float(39.0) == 39.0


def test_sure_float_from_string():
    assert sure_float("39") == 39.0

def test_sure_float_from_string_with_metric():
    assert sure_float("39m") == 39.0
