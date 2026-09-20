from __future__ import annotations

from typing import Iterable


def calculate_forecast_metrics(actual: Iterable[float], predicted: Iterable[float]) -> dict:
    actual_values = list(actual)
    predicted_values = list(predicted)

    if len(actual_values) != len(predicted_values):
        raise ValueError("Actual and predicted series must have the same length.")

    if not actual_values:
        return {"mae": 0.0, "rmse": 0.0, "wape": 0.0}

    absolute_errors = [abs(a - p) for a, p in zip(actual_values, predicted_values)]
    squared_errors = [(a - p) ** 2 for a, p in zip(actual_values, predicted_values)]

    mae = sum(absolute_errors) / len(absolute_errors)
    rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5
    numerator = sum(absolute_errors)
    denominator = sum(abs(v) for v in actual_values)
    wape = 0.0 if denominator == 0 else numerator / denominator

    return {"mae": float(mae), "rmse": float(rmse), "wape": float(wape)}


def calculate_safety_stock(series: Iterable[float], lead_time_days: float, service_level: float) -> dict:
    values = [float(v) for v in series]
    if not values:
        return {
            "average_daily_demand": 0.0,
            "std_dev_demand": 0.0,
            "sigma_lead_time": 0.0,
            "safety_stock": 0.0,
            "reorder_point": 0.0,
            "par_level": 0.0,
        }

    avg_daily = sum(values) / len(values)
    if len(values) == 1:
        std_dev = 0.0
    else:
        mean = sum(values) / len(values)
        std_dev = (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5

    sigma_lead_time = std_dev * (lead_time_days ** 0.5)
    z_score = float(service_level)
    safety_stock = z_score * sigma_lead_time
    lead_time_demand = avg_daily * lead_time_days
    reorder_point = lead_time_demand + safety_stock
    par_level = reorder_point

    return {
        "average_daily_demand": float(avg_daily),
        "std_dev_demand": float(std_dev),
        "sigma_lead_time": float(sigma_lead_time),
        "safety_stock": float(safety_stock),
        "reorder_point": float(reorder_point),
        "par_level": float(par_level),
    }
