def is_adult(age: int) -> bool:
    return age >= 18

def result(number: int) -> bool:
    return 1 + 1 == number

def human(name: str) -> bool:
    return name == 'timur'

def famili (fam: str) -> bool:
    return fam == 'eskiev'

def polindrom(a: str) -> bool:
    c = a.replace(' ', '').lower()
    return c == c[::-1]