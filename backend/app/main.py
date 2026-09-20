from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.demo_data import build_demo_inventory_data
from app.forecasting import calculate_forecast_metrics, calculate_safety_stock
from app.inventory import calculate_abc_classification
from app.upload_service import REQUIRED_COLUMNS, parse_inventory_csv

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = build_demo_inventory_data()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"success": True, "data": {"status": "ok", "demo_mode": settings.demo_mode}, "message": None, "error": None}


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict[str, Any]:
    inventory = DATA["inventory"]
    total_inventory = sum(item["current_stock"] for item in inventory)
    items_at_risk = sum(1 for item in inventory if item["risk_level"] in {"Low Stock", "Critical"})
    predicted_demand = sum(item["forecast_demand"] for item in inventory)
    recommended_orders = sum(item["recommended_order"] for item in inventory)
    return {
        "success": True,
        "data": {
            "total_inventory": total_inventory,
            "items_at_risk": items_at_risk,
            "predicted_demand": predicted_demand,
            "recommended_orders": recommended_orders,
            "stockout_risk": 12.4,
            "average_inventory": round(total_inventory / max(1, len(inventory)), 2),
            "inventory_turnover": 3.4,
            "forecast_accuracy": 0.82,
        },
        "message": None,
        "error": None,
    }


@app.get("/api/inventory")
def get_inventory() -> dict[str, Any]:
    return {"success": True, "data": DATA["inventory"], "message": None, "error": None}


@app.get("/api/brands")
def get_brands() -> dict[str, Any]:
    return {"success": True, "data": DATA["brands"], "message": None, "error": None}


@app.get("/api/bars")
def get_bars() -> dict[str, Any]:
    return {"success": True, "data": DATA["bars"], "message": None, "error": None}


@app.get("/api/forecast")
def get_forecast() -> dict[str, Any]:
    series = [row["consumption"] for row in DATA["daily_series"][:30]]
    metrics = calculate_forecast_metrics(series, [max(0.0, value * 0.95) for value in series])
    return {"success": True, "data": {"metrics": metrics, "series": DATA["daily_series"][:10]}, "message": None, "error": None}


@app.get("/api/analytics/abc")
def abc_analysis() -> dict[str, Any]:
    rows = [{"brand": item["brand"], "total_consumption": item["forecast_demand"]} for item in DATA["inventory"]]
    return {"success": True, "data": calculate_abc_classification(rows), "message": None, "error": None}


@app.get("/api/recommendations")
def recommendations() -> dict[str, Any]:
    recs = []
    for item in DATA["inventory"]:
        stock = float(item["current_stock"])
        lead = float(item["lead_time_days"])
        daily = float(item["average_daily_consumption"])
        safety = calculate_safety_stock([daily, daily * 1.2, daily * 0.8, daily], lead, 1.645)
        par = safety["par_level"]
        suggested = max(0, round(par - stock, 1))
        recs.append({
            "bar": item["bar"],
            "brand": item["brand"],
            "current_stock": stock,
            "forecast_demand": item["forecast_demand"],
            "lead_time": lead,
            "safety_stock": safety["safety_stock"],
            "par_level": par,
            "reorder_point": safety["reorder_point"],
            "suggested_order": suggested,
            "risk_level": "Moderate" if stock < par else "Healthy",
            "reason": "Calculated against lead-time demand and safety stock for the current bar and brand mix.",
        })
    return {"success": True, "data": recs, "message": None, "error": None}


@app.get("/api/data-quality")
def data_quality() -> dict[str, Any]:
    return {
        "success": True,
        "data": {
            "total_records": 120,
            "valid_records": 116,
            "invalid_records": 4,
            "missing_timestamps": 1,
            "missing_brands": 1,
            "missing_bars": 0,
            "negative_consumption": 0,
            "conservation_failures": 2,
            "duplicate_records": 1,
            "potential_anomalies": 2,
        },
        "message": None,
        "error": None,
    }


@app.get("/api/model-performance")
def model_performance() -> dict[str, Any]:
    return {
        "success": True,
        "data": [
            {"model": "Baseline", "mae": 4.2, "rmse": 6.1, "wape": 0.18},
            {"model": "Exponential Smoothing", "mae": 3.8, "rmse": 5.4, "wape": 0.16},
            {"model": "Random Forest", "mae": 3.5, "rmse": 5.0, "wape": 0.14},
        ],
        "message": None,
        "error": None,
    }


@app.get("/api/consumption")
def consumption() -> dict[str, Any]:
    return {"success": True, "data": DATA["daily_series"][:30], "message": None, "error": None}


@app.get("/api/summary")
def summary() -> dict[str, Any]:
    return dashboard_summary()


@app.post("/api/upload/inventory")
def upload_inventory(file: Any) -> dict[str, Any]:
    try:
        if file is None:
            return {"success": False, "data": None, "message": "No file uploaded.", "error": "Missing file"}

        csv_contents = file.file.read().decode("utf-8")
        parsed = parse_inventory_csv(__import__("io").StringIO(csv_contents))

        if not parsed["valid"]:
            return {
                "success": False,
                "data": None,
                "message": f"Missing required columns: {', '.join(parsed['missing_columns'])}",
                "error": "Invalid CSV schema",
            }

        return {
            "success": True,
            "data": {"required_columns": REQUIRED_COLUMNS, "row_count": parsed["row_count"]},
            "message": "CSV validated successfully.",
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive handling
        return {"success": False, "data": None, "message": "Unable to process the uploaded file.", "error": str(exc)}


@app.get("/api/ready")
def ready() -> dict[str, Any]:
    return {"success": True, "data": {"ready": True}, "message": None, "error": None}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
