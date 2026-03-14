
def multiply(a: int, b: int) -> int:
    return a * b

def ret_str():
    return 'какая то строка'


# result = multiply(2, 2) == 4
#
# print(result)
# assert multiply(2, 2) == 4


def duble_list(lst: list[int]) -> list[int]:
    l = [i * i for i in lst]
    return l


if __name__ == '__main__':
    print(duble_list([1, 2, 3]))
