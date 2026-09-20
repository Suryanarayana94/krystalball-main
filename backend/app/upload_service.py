from __future__ import annotations

import csv
from io import StringIO
from typing import Any

REQUIRED_COLUMNS = [
    "Date Time Served",
    "Bar Name",
    "Brand Name",
    "Opening Balance",
    "Purchase",
    "Consumed",
    "Closing Balance",
]


def parse_inventory_csv(file_obj: StringIO) -> dict[str, Any]:
    """Validate and parse an uploaded bar inventory CSV file."""
    reader = csv.DictReader(file_obj)
    headers = list(reader.fieldnames or [])

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in headers
    ]

    rows = []
    if not missing_columns:
        for row in reader:
            cleaned = {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}
            rows.append(cleaned)

    return {
        "valid": not missing_columns,
        "row_count": len(rows),
        "missing_columns": missing_columns,
        "rows": rows,
    }
