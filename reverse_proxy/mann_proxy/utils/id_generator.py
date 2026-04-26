import itertools


class IDGenerator:
    """
    Simple incremental ID generator.
    """

    def __init__(self, start=1):
        self._counter = itertools.count(start)

    def next_id(self):
        return next(self._counter)


# Global generators (optional)
request_id_gen = IDGenerator()
connection_id_gen = IDGenerator()