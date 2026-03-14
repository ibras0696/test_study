from app.logic import is_adult
from app.logic import result
from app.logic import human
from app.logic import famili

def test_is_adult_true() -> None:
    assert is_adult(18) is True

def test_result_true() -> None:
    assert result(2) is True

def test_name_true() -> None:
    assert human('timur') is True

def test_famili_true() -> None:
    assert famili('eskiev') is True

import pytest

def add(a: int, b: int) -> int:
    return a+b

@pytest.mark.parametrize(
    'a, b, expected',
    [
        (1, 2, 3),
        (0, 0, 0),
        (3, 3, 3),
        (5, 7, 1)
    ],
)
def test_add(a: int, b: int, expected: int) -> None:
    assert add(a, b) == expected
from app.logic import polindrom

@pytest.mark.parametrize(
    'a,b',
    [
        ('Анна ', True),
        ('Велик ', False),
        ('Лол ', True),
        ('lkj ', False)
    ],
)
def test_add(a: str, b: bool) -> None:
    assert polindrom(a) == b