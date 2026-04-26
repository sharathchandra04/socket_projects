import time


def now():
    """
    Wall clock time (for logging only)
    """
    return time.time()


def monotonic_now():
    """
    High precision timer for latency measurement (DO NOT use time.time)
    """
    return time.monotonic()


def elapsed(start, end=None):
    """
    Returns elapsed time in seconds
    """
    if end is None:
        end = monotonic_now()
    return end - start


def ms(seconds):
    """
    Convert seconds → milliseconds
    """
    return seconds * 1000