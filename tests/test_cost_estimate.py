import json
from decimal import Decimal
from pathlib import Path

from scripts.calculate_monthly_cost import calculate


ESTIMATE = Path(__file__).parents[1] / "costs" / "aws-us-east-1.json"


def test_documented_monthly_and_one_time_totals() -> None:
    data = json.loads(ESTIMATE.read_text(encoding="utf-8"))

    _, monthly_total = calculate(data["monthly_items"])
    _, one_time_total = calculate(data["one_time_items"])

    assert monthly_total == Decimal("736.54")
    assert one_time_total == Decimal("3.204")


def test_estimate_contains_non_obvious_costs() -> None:
    data = json.loads(ESTIMATE.read_text(encoding="utf-8"))
    services = {item["service"] for item in data["monthly_items"]}

    assert "RDS additional backup storage" in services
    assert "Data transfer out to Power BI" in services
    assert "S3 PUT/COPY/POST/LIST" in services
    assert "CloudWatch Logs ingestion" in services
