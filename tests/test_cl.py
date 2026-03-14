import pytest

from app.calc import multiply


def test_multiply():
    a = 10
    b = 2
    result = 20
    assert multiply(a, b) == result


@pytest.mark.parametrize(
    'a, b, result',
    [
        (1, 2, 2), # 1
        (2, 2, 4), # 2

    ]
)
def test_multiply_parametrize(a, b, result):
    assert multiply(a, b) == result