"""Valida CO-PA desde Landing, calcula margen y publica CSV en Curated."""

import argparse
import csv
import io
from decimal import Decimal, InvalidOperation

import boto3
from botocore.exceptions import ClientError

from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    CURATED_BUCKET,
    LANDING_BUCKET,
    ROOT,
)

REQUIRED_FIELDS = {
    "document_number",
    "fiscal_year",
    "fiscal_period",
    "company_code",
    "company_name",
    "profit_center",
    "profit_center_description",
    "revenue",
    "cost",
    "currency",
    "source_updated_at",
}


def transform_row(row: dict[str, str]) -> dict[str, str]:
    missing = REQUIRED_FIELDS - row.keys()
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")

    try:
        revenue = Decimal(row["revenue"])
        cost = Decimal(row["cost"])
        period = int(row["fiscal_period"])
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Registro inválido {row.get('document_number')}: {error}") from error

    if not 1 <= period <= 16:
        raise ValueError(f"Período inválido: {period}")
    if revenue < 0 or cost < 0:
        raise ValueError("Revenue y cost deben ser no negativos")

    transformed = dict(row)
    transformed["margin"] = f"{revenue - cost:.2f}"
    transformed["margin_pct"] = f"{((revenue - cost) / revenue * 100) if revenue else Decimal(0):.2f}"
    return transformed


def client():
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def ensure_bucket(s3, name: str) -> None:
    try:
        s3.head_bucket(Bucket=name)
    except ClientError:
        s3.create_bucket(Bucket=name)
        print(f"Bucket creado: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-type", choices=["initial", "delta"], required=True)
    args = parser.parse_args()

    s3 = client()
    ensure_bucket(s3, CURATED_BUCKET)
    prefix = f"copa/load_type={args.load_type}/"
    objects = s3.list_objects_v2(Bucket=LANDING_BUCKET, Prefix=prefix).get("Contents", [])
    if not objects:
        raise SystemExit(f"No hay objetos en s3://{LANDING_BUCKET}/{prefix}")

    output_dir = ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in objects:
        source_key = item["Key"]
        source_text = s3.get_object(Bucket=LANDING_BUCKET, Key=source_key)["Body"].read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(source_text))
        transformed = [transform_row(row) for row in reader]
        if not transformed:
            continue

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(transformed[0].keys()))
        writer.writeheader()
        writer.writerows(transformed)

        filename = source_key.rsplit("/", 1)[-1].replace(".csv", "_curated.csv")
        local_path = output_dir / filename
        local_path.write_text(output.getvalue(), encoding="utf-8")
        target_key = f"copa/load_type={args.load_type}/{filename}"
        s3.put_object(
            Bucket=CURATED_BUCKET,
            Key=target_key,
            Body=output.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )
        print(f"Procesado: {source_key} -> s3://{CURATED_BUCKET}/{target_key} ({len(transformed)} registros)")


if __name__ == "__main__":
    main()
