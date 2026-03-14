# lst = [1, 5, 7, 10, 14, 25]  # 10_000_000  | 4_274_354
#
target = 457_435
lst = [i for i in range(1, 1_000_000)]


def search_func(lst: list[int], target: int):
    start = 0
    end = len(lst) - 1

    for i in range(len(lst)):
        if lst[start] == target:
            return 'Нашел'

        if lst[end] == target:
            return 'Нашел'

        start += 1
        end -= 1

    return 'Не нашел твое число'


search_func(lst, target)
