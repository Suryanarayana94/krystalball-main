import math

from app.forecasting import calculate_forecast_metrics, calculate_safety_stock
from app.inventory import calculate_abc_classification


def test_calculate_safety_stock_for_positive_series():
    series = [10, 12, 9, 13, 11, 10, 12]
    result = calculate_safety_stock(series, lead_time_days=3, service_level=1.645)
    assert result["average_daily_demand"] > 0
    assert result["safety_stock"] >= 0
    assert result["par_level"] >= result["reorder_point"]


def test_wape_handles_zero_demand_series_safely():
    actual = [0, 0, 0]
    predicted = [0, 0, 0]
    metrics = calculate_forecast_metrics(actual, predicted)
    assert metrics["wape"] == 0.0


def test_abc_classification_returns_class_labels():
    data = [
        {"brand": "A", "total_consumption": 100},
        {"brand": "B", "total_consumption": 50},
        {"brand": "C", "total_consumption": 20},
    ]
    result = calculate_abc_classification(data)
    assert {row["brand"] for row in result} == {"A", "B", "C"}
    assert {row["abc_class"] for row in result}.issubset({"A", "B", "C"})


def test_safety_stock_for_constant_series_is_non_negative():
    series = [5, 5, 5, 5]
    result = calculate_safety_stock(series, lead_time_days=2, service_level=2.326)
    assert result["safety_stock"] >= 0
    assert math.isfinite(result["sigma_lead_time"])
