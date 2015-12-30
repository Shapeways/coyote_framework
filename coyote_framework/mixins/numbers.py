__author__ = 'dkobozev'

import decimal


def parse_decimal(s):
    return decimal.Decimal(''.join([char for char in s if char in '0123456789.']))


def parse_int(s):
    return int(''.join([char for char in s if char in '0123456789.']))
