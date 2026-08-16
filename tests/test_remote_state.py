from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = (ROOT / "iac" / "backend.tf").read_text(encoding="utf-8")
BOOTSTRAP = (ROOT / "iac" / "bootstrap-state" / "main.tf").read_text(encoding="utf-8")


def test_main_stack_declares_partial_s3_backend():
    assert 'backend "s3" {}' in BACKEND
    assert "access_key" not in BACKEND
    assert "secret_key" not in BACKEND


def test_state_bucket_is_private_versioned_encrypted_and_protected():
    assert 'resource "aws_s3_bucket_public_access_block" "terraform_state"' in BOOTSTRAP
    assert 'status = "Enabled"' in BOOTSTRAP
    assert 'sse_algorithm = "AES256"' in BOOTSTRAP
    assert 'prevent_destroy = true' in BOOTSTRAP
    assert 'variable = "aws:SecureTransport"' in BOOTSTRAP


def test_dynamodb_lock_table_has_required_controls():
    assert 'resource "aws_dynamodb_table" "terraform_locks"' in BOOTSTRAP
    assert 'hash_key     = "LockID"' in BOOTSTRAP
    assert 'billing_mode = "PAY_PER_REQUEST"' in BOOTSTRAP
    assert "point_in_time_recovery" in BOOTSTRAP
    assert "server_side_encryption" in BOOTSTRAP
