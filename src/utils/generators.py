import random

from .sample_classes import Context

def generate_month():
    return random.randint(1, 12)


def generate_day():
    return random.randint(1, 28)


def generate_date():
    month = generate_month
    day = generate_day
    date = f"2018-{month}-{day}"
    return date


def generate_current(data):
    date = generate_date()
    try:
        current = data.loc[:, date, :]
        return current
    except KeyError:
        return None

def generate_ctx():
    pass