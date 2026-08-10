"""Carga archivos Curated en PostgreSQL con upserts idempotentes."""

import argparse
import csv
from pathlib import Path

import psycopg2

from settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    ROOT,
)


def upsert_dimension(cursor, table: str, code_column: str, code: str, description_column: str, description: str) -> int:
    key_column = f"{code_column}_key"
    cursor.execute(
        f"""
        INSERT INTO dwh.{table} ({code_column}, {description_column})
        VALUES (%s, %s)
        ON CONFLICT ({code_column}) DO UPDATE
        SET {description_column} = EXCLUDED.{description_column}
        RETURNING {key_column}
        """,
        (code, description),
    )
    return cursor.fetchone()[0]


def load_file(cursor, csv_path: Path) -> int:
    loaded = 0
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            company_key = upsert_dimension(
                cursor,
                "dim_company_code",
                "company_code",
                row["company_code"],
                "company_name",
                row["company_name"],
            )
            profit_center_key = upsert_dimension(
                cursor,
                "dim_profit_center",
                "profit_center",
                row["profit_center"],
                "description",
                row["profit_center_description"],
            )
            cursor.execute(
                """
                INSERT INTO dwh.fact_copa (
                    document_number, fiscal_year, fiscal_period,
                    company_code_key, profit_center_key,
                    revenue, cost, currency, source_updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_number, fiscal_year, fiscal_period, company_code_key)
                DO UPDATE SET
                    profit_center_key = EXCLUDED.profit_center_key,
                    revenue = EXCLUDED.revenue,
                    cost = EXCLUDED.cost,
                    currency = EXCLUDED.currency,
                    source_updated_at = EXCLUDED.source_updated_at,
                    loaded_at = CURRENT_TIMESTAMP
                """,
                (
                    row["document_number"],
                    int(row["fiscal_year"]),
                    int(row["fiscal_period"]),
                    company_key,
                    profit_center_key,
                    row["revenue"],
                    row["cost"],
                    row["currency"],
                    row["source_updated_at"],
                ),
            )
            loaded += 1
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    csv_path = args.file if args.file.is_absolute() else ROOT / args.file
    if not csv_path.exists():
        raise SystemExit(f"Archivo no encontrado: {csv_path}")

    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    ) as connection:
        with connection.cursor() as cursor:
            count = load_file(cursor, csv_path)
    print(f"Cargado: {csv_path.name} ({count} registros procesados)")


if __name__ == "__main__":
    main()
