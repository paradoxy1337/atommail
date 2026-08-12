"""Генерация случайных данных для регистрации: имена, юзернеймы, пароли."""

import random
import string

FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy",
    "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara",
    "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty",
    "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna",
    "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie",
    "Rebecca", "Sharon", "Laura", "Cynthia", "Amy", "Kathleen", "Angela",
    "Shirley", "Brenda", "Emma", "Anna", "Pamela", "Nicole", "Samantha",
    "Katherine", "Christine", "Helen", "Debra", "Rachel", "Carolyn",
    "Janet", "Maria", "Catherine", "Heather", "Diane", "Olivia", "Julie",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
    "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
    "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
    "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez", "Wood",
    "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", "Price",
]


def random_first_name() -> str:
    return random.choice(FIRST_NAMES)


def random_last_name() -> str:
    return random.choice(LAST_NAMES)


def random_username(first: str = "", last: str = "") -> str:
    """Случайный юзернейм 5-21 символов: буквы, цифры, точки."""
    first = (first or random_first_name()).lower()
    last = (last or random_last_name()).lower()
    suffix = "".join(random.choices(string.digits, k=random.randint(2, 5)))
    pattern = random.choice([
        f"{first}.{last}",
        f"{first}{last}",
        f"{first}_{last}",
        f"{first}.{last}{suffix}",
        f"{first}{suffix}",
        f"{first[0]}.{last}{suffix}",
        f"{last}.{first}{suffix}",
        f"{first}{random.randint(80, 99)}{suffix[:2]}",
    ])
    # Ограничение длины 5-21 символ
    pattern = pattern[:21]
    if len(pattern) < 5:
        pattern += suffix
    return pattern.lower()


def random_password() -> str:
    """Случайный пароль: буквы обоих регистров + цифры + спецсимвол."""
    upper = random.choices(string.ascii_uppercase, k=3)
    lower = random.choices(string.ascii_lowercase, k=4)
    digits = random.choices(string.digits, k=2)
    special = random.choice("!@#$%^&*")
    pool = upper + lower + digits + [special]
    random.shuffle(pool)
    return "".join(pool)
