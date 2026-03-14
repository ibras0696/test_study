import pytest


@pytest.fixture
def number() -> int:
    return 10


@pytest.fixture
def lst_double() -> list[int]:
    return [1, 2, 3, 4, 5]
