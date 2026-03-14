from app.calc import duble

def test_calc(calc):
    assert duble(calc) == [4, 9, 16]
    print(duble(calc))
