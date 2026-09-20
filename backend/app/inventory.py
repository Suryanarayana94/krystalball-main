from __future__ import annotations

from typing import Iterable


def calculate_abc_classification(data: Iterable[dict]) -> list[dict]:
    rows = list(data)
    if not rows:
        return []

    total = sum(float(row.get("total_consumption", 0)) for row in rows)
    result = []
    for row in rows:
        value = float(row.get("total_consumption", 0))
        share = 0.0 if total == 0 else value / total
        if share >= 0.8:
            abc_class = "A"
        elif share >= 0.15:
            abc_class = "B"
        else:
            abc_class = "C"
        result.append({
            "brand": row.get("brand"),
            "total_consumption": value,
            "percentage_contribution": share,
            "abc_class": abc_class,
        })

    return result
