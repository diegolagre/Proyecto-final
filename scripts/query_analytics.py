"""Consulta de control para validar el Data Warehouse local."""

import psycopg2

from settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

QUERY = """
SELECT
    c.company_code,
    f.fiscal_period,
    COUNT(*) AS records,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.revenue - f.cost), 2) AS margin
FROM dwh.fact_copa f
JOIN dwh.dim_company_code c USING (company_code_key)
GROUP BY c.company_code, f.fiscal_period
ORDER BY c.company_code, f.fiscal_period
"""


def main() -> None:
    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(QUERY)
            rows = cursor.fetchall()

    print("Sociedad | Período | Registros | Ingresos | Margen")
    for company, period, records, revenue, margin in rows:
        print(f"{company:8} | {period:7} | {records:9} | {revenue:8} | {margin}")


if __name__ == "__main__":
    main()
