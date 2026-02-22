def add(a: int, b: int) -> int:
    """
    Функция для сумирования чисел
    :param a: число
    :param b: число
    :return: Общую сумму чисел
    """
    return a + b


def is_adult(age: int) -> bool:
    """
    Проверяет, совершеннолетний ли человек по возрасту.

    Args:
        age (int): Возраст человека.

    Returns:
        bool: True если age >= 18, иначе False.
    """
    return age >= 18
