from app.logic import is_adult


def test_is_adult_true() -> None:
    assert is_adult(18) is True