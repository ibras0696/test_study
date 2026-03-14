import pytest
@pytest.fixture
def number() -> int:
    return 10

@pytest.fixture
def calc() -> list:
    return [2, 3, 4]

