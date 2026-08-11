"""Crea y verifica la línea base AWS local de forma idempotente.

Reutiliza los patrones de ``iam_demo.py`` y ``vpc_demo.py`` del repositorio
cloud-foundations-lab. LocalStack modela la API y el grafo de recursos; no
reproduce todos los controles de seguridad ni el tráfico de AWS real.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    CURATED_BUCKET,
    LANDING_BUCKET,
    LOCAL_LOG_GROUP,
    LOCAL_ROLE_NAME,
    LOCAL_SECRET_NAME,
    LOCAL_VPC_NAME,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


CLIENT_ARGS = {
    "endpoint_url": AWS_ENDPOINT_URL,
    "region_name": AWS_REGION,
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
}


def client(service: str):
    return boto3.client(service, **CLIENT_ARGS)


def error_code(error: ClientError) -> str:
    return str(error.response.get("Error", {}).get("Code", ""))


def already_exists(error: ClientError) -> bool:
    code = error_code(error).lower()
    return "already" in code or code in {"entityalreadyexists", "resourceexistsexception"}


def tag(ec2, resource_id: str, name: str, **extra: str) -> None:
    tags = [{"Key": "Name", "Value": name}, {"Key": "Project", "Value": "sap-analytics-migration"}]
    tags.extend({"Key": key, "Value": value} for key, value in extra.items())
    ec2.create_tags(Resources=[resource_id], Tags=tags)


def named(items: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for item in items:
        if any(tag_item.get("Key") == "Name" and tag_item.get("Value") == name for tag_item in item.get("Tags", [])):
            return item
    return None


def ensure_buckets() -> None:
    s3 = client("s3")
    for bucket in (LANDING_BUCKET, CURATED_BUCKET):
        try:
            s3.head_bucket(Bucket=bucket)
            print(f"S3: bucket existente {bucket}")
        except ClientError:
            s3.create_bucket(Bucket=bucket)
            print(f"S3: bucket creado {bucket}")


def ensure_role() -> None:
    iam = client("iam")
    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    }
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{LANDING_BUCKET}", f"arn:aws:s3:::{CURATED_BUCKET}"],
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:GetObjectVersion"],
                "Resource": f"arn:aws:s3:::{LANDING_BUCKET}/*",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:PutObject"],
                "Resource": f"arn:aws:s3:::{CURATED_BUCKET}/*",
            },
        ],
    }
    try:
        iam.create_role(
            RoleName=LOCAL_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust),
            Description="Rol ETL local con acceso mínimo a Landing y Curated",
        )
        print(f"IAM: rol creado {LOCAL_ROLE_NAME}")
    except ClientError as error:
        if not already_exists(error):
            raise
        print(f"IAM: rol existente {LOCAL_ROLE_NAME}")
    iam.put_role_policy(
        RoleName=LOCAL_ROLE_NAME,
        PolicyName="S3LandingToCurated",
        PolicyDocument=json.dumps(policy),
    )


def ensure_network() -> None:
    ec2 = client("ec2")
    vpc = named(ec2.describe_vpcs()["Vpcs"], LOCAL_VPC_NAME)
    if vpc is None:
        vpc = ec2.create_vpc(CidrBlock="10.20.0.0/16")["Vpc"]
        tag(ec2, vpc["VpcId"], LOCAL_VPC_NAME)
        print(f"VPC: creada {vpc['VpcId']}")
    else:
        print(f"VPC: existente {vpc['VpcId']}")

    vpc_id = vpc["VpcId"]
    existing_subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
    for index, cidr in enumerate(("10.20.10.0/24", "10.20.20.0/24"), start=1):
        subnet_name = f"{LOCAL_VPC_NAME}-private-{index}"
        if named(existing_subnets, subnet_name):
            continue
        subnet = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr,
            AvailabilityZone=f"{AWS_REGION}{'a' if index == 1 else 'b'}",
        )["Subnet"]
        tag(ec2, subnet["SubnetId"], subnet_name, Tier="private")

    groups = ec2.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["SecurityGroups"]
    by_name = {group["GroupName"]: group["GroupId"] for group in groups}
    for group_name, description in (
        ("analytics-etl", "Worker ETL local"),
        ("analytics-database", "PostgreSQL privado local"),
    ):
        if group_name not in by_name:
            by_name[group_name] = ec2.create_security_group(
                VpcId=vpc_id,
                GroupName=group_name,
                Description=description,
            )["GroupId"]
            tag(ec2, by_name[group_name], group_name)

    try:
        ec2.authorize_security_group_ingress(
            GroupId=by_name["analytics-database"],
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort": 5432,
                "ToPort": 5432,
                "UserIdGroupPairs": [{"GroupId": by_name["analytics-etl"]}],
            }],
        )
    except ClientError as error:
        if "duplicate" not in str(error).lower():
            raise


def ensure_secret() -> None:
    secrets = client("secretsmanager")
    value = json.dumps({
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "dbname": POSTGRES_DB,
        "username": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
    })
    try:
        secrets.create_secret(Name=LOCAL_SECRET_NAME, SecretString=value)
        print(f"Secrets Manager: secreto creado {LOCAL_SECRET_NAME}")
    except ClientError as error:
        if error_code(error) != "ResourceExistsException":
            raise
        secrets.put_secret_value(SecretId=LOCAL_SECRET_NAME, SecretString=value)
        print(f"Secrets Manager: secreto actualizado {LOCAL_SECRET_NAME}")


def ensure_log_group() -> None:
    logs = client("logs")
    groups = logs.describe_log_groups(logGroupNamePrefix=LOCAL_LOG_GROUP)["logGroups"]
    if any(group["logGroupName"] == LOCAL_LOG_GROUP for group in groups):
        print(f"CloudWatch Logs: grupo existente {LOCAL_LOG_GROUP}")
        return
    logs.create_log_group(logGroupName=LOCAL_LOG_GROUP)
    logs.put_retention_policy(logGroupName=LOCAL_LOG_GROUP, retentionInDays=30)
    print(f"CloudWatch Logs: grupo creado {LOCAL_LOG_GROUP}")


def verify() -> list[str]:
    checks: list[tuple[str, bool]] = []
    s3 = client("s3")
    checks.append(("S3", all(bucket in {item["Name"] for item in s3.list_buckets()["Buckets"]} for bucket in (LANDING_BUCKET, CURATED_BUCKET))))
    checks.append(("IAM", client("iam").get_role(RoleName=LOCAL_ROLE_NAME)["Role"]["RoleName"] == LOCAL_ROLE_NAME))
    checks.append(("VPC/EC2", named(client("ec2").describe_vpcs()["Vpcs"], LOCAL_VPC_NAME) is not None))
    checks.append(("Secrets Manager", client("secretsmanager").describe_secret(SecretId=LOCAL_SECRET_NAME)["Name"] == LOCAL_SECRET_NAME))
    groups = client("logs").describe_log_groups(logGroupNamePrefix=LOCAL_LOG_GROUP)["logGroups"]
    checks.append(("CloudWatch Logs", any(group["logGroupName"] == LOCAL_LOG_GROUP for group in groups)))

    failed = []
    for service, ok in checks:
        print(f"{'OK' if ok else 'ERROR'}  {service}")
        if not ok:
            failed.append(service)
    return failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Sólo verifica los recursos existentes")
    args = parser.parse_args()

    if not args.check:
        ensure_buckets()
        ensure_role()
        ensure_network()
        ensure_secret()
        ensure_log_group()

    failed = verify()
    if failed:
        raise SystemExit(f"Fallaron servicios: {', '.join(failed)}")
    print("Línea base local verificada: 5 servicios AWS.")


if __name__ == "__main__":
    main()
