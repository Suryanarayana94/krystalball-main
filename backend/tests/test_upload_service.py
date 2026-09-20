import io

from app.upload_service import parse_inventory_csv


def test_parse_inventory_csv_accepts_required_columns():
    csv_text = (
        "Date Time Served,Bar Name,Brand Name,Opening Balance,Purchase,Consumed,Closing Balance\n"
        "2026-09-01 18:00,Lobby Bar,Gin,40,10,12,38\n"
        "2026-09-01 18:30,Rooftop Bar,Vodka,25,5,8,22\n"
    )

    result = parse_inventory_csv(io.StringIO(csv_text))

    assert result["valid"] is True
    assert result["row_count"] == 2
    assert result["missing_columns"] == []
    assert result["rows"][0]["Brand Name"] == "Gin"


def test_parse_inventory_csv_reports_missing_required_columns():
    csv_text = "Date Time Served,Bar Name,Brand Name,Opening Balance\n2026-09-01 18:00,Lobby Bar,Gin,40\n"

    result = parse_inventory_csv(io.StringIO(csv_text))

    assert result["valid"] is False
    assert "Purchase" in result["missing_columns"]
