import re


def clean_money(value):
    value = value.replace('.', '').replace(',', '.')
    matches = re.findall('\d+\.\d+', value)
    return matches[0] if matches else 0
