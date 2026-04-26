import time


def now():
    """
    Current timestamp (seconds)
    """
    return time.time()


def now_ms():
    """
    Current timestamp in milliseconds
    """
    return int(time.time() * 1000)


def elapsed(start_time):
    """
    Time elapsed since start_time (seconds)
    """
    return time.time() - start_time


def elapsed_ms(start_time):
    """
    Time elapsed in milliseconds
    """
    return int((time.time() - start_time) * 1000)   