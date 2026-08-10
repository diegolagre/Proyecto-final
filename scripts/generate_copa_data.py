"""Genera datos CO-PA sintéticos y reproducibles, sin información productiva."""

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from settings import ROOT

FIELDS = [
    "document_number",
    "fiscal_year",
    "fiscal_period",
    "company_code",
    "company_name",
    "profit_center",
    "profit_center_description",
    "customer_id",
    "product_id",
    "revenue",
    "cost",
    "currency",
    "source_updated_at",
]


def build_rows(count: int, start_id: int, seed: int) -> list[dict[str, str | int]]:
    rng = random.Random(seed)
    base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    companies = [("AR01", "Compañía Modelo Argentina"), ("UY01", "Compañía Modelo Uruguay")]
    profit_centers = [("PC100", "Consumo Masivo"), ("PC200", "Canal Mayorista"), ("PC300", "Exportación")]
    rows = []

    for offset in range(count):
        record_id = start_id + offset
        company_code, company_name = rng.choice(companies)
        profit_center, profit_center_description = rng.choice(profit_centers)
        revenue = round(rng.uniform(1_000, 75_000), 2)
        margin_ratio = rng.uniform(0.12, 0.42)
        cost = round(revenue * (1 - margin_ratio), 2)
        period = ((record_id - 1) % 12) + 1
        updated_at = base_time + timedelta(days=offset, minutes=record_id)

        rows.append(
            {
                "document_number": f"DOC{record_id:010d}",
                "fiscal_year": 2025,
                "fiscal_period": period,
                "company_code": company_code,
                "company_name": company_name,
                "profit_center": profit_center,
                "profit_center_description": profit_center_description,
                "customer_id": f"C{rng.randint(1, 500):06d}",
                "product_id": f"MAT{rng.randint(1, 120):05d}",
                "revenue": f"{revenue:.2f}",
                "cost": f"{cost:.2f}",
                "currency": "ARS" if company_code == "AR01" else "UYU",
                "source_updated_at": updated_at.isoformat().replace("+00:00", "Z"),
            }
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generado: {path.relative_to(ROOT)} ({len(rows)} registros)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial-rows", type=int, default=1_000)
    parser.add_argument("--delta-rows", type=int, default=50)
    args = parser.parse_args()

    write_csv(
        ROOT / "data" / "source" / "copa_initial.csv",
        build_rows(args.initial_rows, start_id=1, seed=20250809),
    )
    write_csv(
        ROOT / "data" / "source" / "copa_delta_001.csv",
        build_rows(args.delta_rows, start_id=args.initial_rows + 1, seed=20250810),
    )


if __name__ == "__main__":
    main()
