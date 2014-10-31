# -*- coding: utf-8 -*-

from functools import wraps

class ConstraintException(Exception):
    pass

class PrecedenceException(Exception):
    pass

def memoized(func):
    memo = {}
    @wraps(func)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = func(*args)
            memo[args] = rv
            return rv
    return wrapper
