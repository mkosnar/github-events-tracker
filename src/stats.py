from datetime import datetime
from itertools import pairwise
from typing import Collection


def average_dt_difference(times: Collection[datetime]) -> float:
    """
    Computes the average delay between consecutive datetimes.
    Returns 0 for less than 2 datetimes.

    Args:
        times: sorted colection of datetimes(requires __len__, __iter__)

    Returns:
        average difference in seconds
    """
    if len(times) <= 1:
        return 0

    return sum((a-b).total_seconds() for a, b in pairwise(times)) / (len(times)-1)
