import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

LANDING_BUCKET = os.getenv(
    "LANDING_BUCKET", "sap-analytics-migration-dev-landing"
)
CURATED_BUCKET = os.getenv(
    "CURATED_BUCKET", "sap-analytics-migration-dev-curated"
)
LOCAL_ROLE_NAME = os.getenv("LOCAL_ROLE_NAME", "sap-analytics-migration-dev-etl-role")
LOCAL_VPC_NAME = os.getenv("LOCAL_VPC_NAME", "sap-analytics-migration-dev-vpc")
LOCAL_SECRET_NAME = os.getenv(
    "LOCAL_SECRET_NAME", "sap-analytics-migration/dev/postgres"
)
LOCAL_LOG_GROUP = os.getenv("LOCAL_LOG_GROUP", "/sap-analytics-migration/dev/etl")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "analytics_app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "local_dev_only")
