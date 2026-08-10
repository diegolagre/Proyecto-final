import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from etl_copa import transform_row


def valid_row():
    return {
        "document_number": "DOC0000000001",
        "fiscal_year": "2025",
        "fiscal_period": "1",
        "company_code": "AR01",
        "company_name": "Compañía Modelo Argentina",
        "profit_center": "PC100",
        "profit_center_description": "Consumo Masivo",
        "revenue": "1000.00",
        "cost": "700.00",
        "currency": "ARS",
        "source_updated_at": "2025-01-01T00:00:00Z",
    }


def test_transform_calculates_margin():
    transformed = transform_row(valid_row())
    assert transformed["margin"] == "300.00"
    assert transformed["margin_pct"] == "30.00"


def test_transform_rejects_invalid_period():
    row = valid_row()
    row["fiscal_period"] = "17"
    with pytest.raises(ValueError, match="Período inválido"):
        transform_row(row)


def test_transform_rejects_negative_amounts():
    row = valid_row()
    row["cost"] = "-1"
    with pytest.raises(ValueError, match="no negativos"):
        transform_row(row)
