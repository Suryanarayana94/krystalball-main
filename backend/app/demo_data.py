from __future__ import annotations

from datetime import date, timedelta


def build_demo_inventory_data():
    properties = [
        {"id": 1, "name": "Harbor Grand"},
        {"id": 2, "name": "Skyline Suites"},
    ]

    bars = [
        {"id": 1, "property_id": 1, "name": "Lobby Bar"},
        {"id": 2, "property_id": 1, "name": "Rooftop Bar"},
        {"id": 3, "property_id": 2, "name": "Pool Bar"},
    ]

    brands = [
        {"id": 1, "name": "Gin", "category": "Spirits"},
        {"id": 2, "name": "Vodka", "category": "Spirits"},
        {"id": 3, "name": "Whiskey", "category": "Spirits"},
        {"id": 4, "name": "Beer", "category": "Beer"},
        {"id": 5, "name": "Wine", "category": "Wine"},
    ]

    inventory = []
    brand_profiles = {
        1: {"daily": 7, "lead_time": 3, "current": 35, "service": 1.645},
        2: {"daily": 6, "lead_time": 3, "current": 28, "service": 1.645},
        3: {"daily": 4, "lead_time": 4, "current": 24, "service": 2.326},
        4: {"daily": 18, "lead_time": 2, "current": 70, "service": 1.645},
        5: {"daily": 3, "lead_time": 5, "current": 20, "service": 1.645},
    }

    for bar in bars:
        for brand in brands:
            profile = brand_profiles[brand["id"]]
            inventory.append({
                "bar": bar["name"],
                "bar_id": bar["id"],
                "brand": brand["name"],
                "brand_id": brand["id"],
                "current_stock": profile["current"],
                "average_daily_consumption": profile["daily"],
                "lead_time_days": profile["lead_time"],
                "safety_stock": round(profile["daily"] * profile["lead_time"] * 0.25, 1),
                "recommended_par": profile["current"],
                "reorder_point": max(1, round(profile["daily"] * profile["lead_time"], 1)),
                "risk_level": "Healthy",
                "stock_status": "Healthy",
                "forecast_demand": profile["daily"] * 7,
                "recommended_order": max(0, profile["current"] - profile["daily"] * 2),
            })

    daily_series = []
    base_day = date(2026, 1, 1)
    for bar in bars:
        for brand in brands:
            profile = brand_profiles[brand["id"]]
            for idx in range(120):
                d = base_day + timedelta(days=idx)
                weekend_boost = 1.5 if d.weekday() >= 5 else 1.0
                demand = round(profile["daily"] * weekend_boost + (idx % 7) * 0.3, 2)
                if idx % 17 == 0:
                    demand *= 1.8
                daily_series.append({
                    "bar": bar["name"],
                    "bar_id": bar["id"],
                    "brand": brand["name"],
                    "brand_id": brand["id"],
                    "date": d.isoformat(),
                    "consumption": demand,
                })

    return {"properties": properties, "bars": bars, "brands": brands, "inventory": inventory, "daily_series": daily_series}
