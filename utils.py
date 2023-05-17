"""Utilities module.

This module contains custom all purpouse utilities.
"""

from time import perf_counter


def delay(seconds: float) -> None:
    """
    This function waits until the set time has passed.
    """
    start_time = perf_counter()
    while perf_counter() < start_time + seconds:
        pass
