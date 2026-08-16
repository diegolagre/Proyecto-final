from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_TF = (ROOT / "iac" / "main.tf").read_text(encoding="utf-8")
NETWORKING_TF = (ROOT / "iac" / "networking.tf").read_text(encoding="utf-8")


def test_etl_security_group_has_no_open_egress():
    assert 'cidr_blocks = ["0.0.0.0/0"]' not in MAIN_TF
    etl_sg = MAIN_TF.split('resource "aws_security_group" "etl"', 1)[1]
    etl_sg = etl_sg.split('resource "aws_security_group" "database"', 1)[0]
    assert "egress {" not in etl_sg


def test_etl_egress_uses_only_database_and_private_endpoints():
    assert 'resource "aws_vpc_security_group_egress_rule" "etl_to_database"' in NETWORKING_TF
    assert 'referenced_security_group_id = aws_security_group.database.id' in NETWORKING_TF
    assert 'resource "aws_vpc_security_group_egress_rule" "etl_to_interface_endpoints"' in NETWORKING_TF
    assert 'referenced_security_group_id = aws_security_group.vpc_endpoints[0].id' in NETWORKING_TF
    assert 'resource "aws_vpc_security_group_egress_rule" "etl_to_s3"' in NETWORKING_TF
    assert 'prefix_list_id    = aws_vpc_endpoint.s3[0].prefix_list_id' in NETWORKING_TF


def test_required_private_endpoints_are_declared():
    assert 'vpc_endpoint_type = "Gateway"' in NETWORKING_TF
    for service in ("secretsmanager", "logs", "monitoring"):
        assert f'"{service}"' in NETWORKING_TF
