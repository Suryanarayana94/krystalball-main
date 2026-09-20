from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Hotel Bar Inventory Forecasting"
    debug: bool = True
    default_lead_time_days: int = 3
    default_service_level: float = 1.645
    forecast_horizon_days: int = 14
    demo_mode: bool = True


settings = Settings()
