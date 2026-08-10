"""Simula SAP SLT depositando una extracción CSV en S3 Landing."""

import argparse
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    LANDING_BUCKET,
    ROOT,
)


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def ensure_bucket(client, name: str) -> None:
    try:
        client.head_bucket(Bucket=name)
    except ClientError:
        client.create_bucket(Bucket=name)
        print(f"Bucket creado: {name}")


def upload_if_changed(client, source: Path, key: str) -> None:
    content = source.read_bytes()
    try:
        existing = client.get_object(Bucket=LANDING_BUCKET, Key=key)["Body"].read()
        if existing == content:
            print(f"Sin cambios: s3://{LANDING_BUCKET}/{key}")
            return
    except client.exceptions.NoSuchKey:
        pass

    client.put_object(
        Bucket=LANDING_BUCKET,
        Key=key,
        Body=content,
        ContentType="text/csv",
        Metadata={"source-system": "sap-ecc-synthetic", "extractor": "slt-simulator"},
    )
    print(f"Replicado: {source.name} -> s3://{LANDING_BUCKET}/{key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--load-type", choices=["initial", "delta"], required=True)
    args = parser.parse_args()

    source = args.file if args.file.is_absolute() else ROOT / args.file
    if not source.exists():
        raise SystemExit(f"Archivo no encontrado: {source}")

    client = s3_client()
    ensure_bucket(client, LANDING_BUCKET)
    key = f"copa/load_type={args.load_type}/{source.name}"
    upload_if_changed(client, source, key)


if __name__ == "__main__":
    main()
