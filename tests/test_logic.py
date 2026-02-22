from app.logic import add, is_adult


def test_add():
    a = 10
    b = 20

    result = add(a, b)

    assert result == 30


def test_is_adult_true() -> None:
    """
    Тест: возраст 18+ должен считаться совершеннолетним.
    """
    assert is_adult(18) is True
