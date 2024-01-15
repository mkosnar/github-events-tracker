from datetime import datetime
from itertools import pairwise
from typing import Collection


def average_dt_difference(times: Collection[datetime]) -> float:
    if len(times) <= 1:
        return 0

    return sum((a-b).total_seconds() for a, b in pairwise(times)) / (len(times)-1)
