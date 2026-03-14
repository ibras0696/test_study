from app.calc import multiply


def test_multiply_positive(number):
    print(number, '_'*10)
    assert multiply(number, 2) == 20


def test_multiply_not_zero(number):
    print(number, '_' * 10)
    assert multiply(number, 3) != 0