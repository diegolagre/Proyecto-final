from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPUTE_TF = (ROOT / "iac" / "compute.tf").read_text(encoding="utf-8")


def test_terraform_does_not_reset_autoscaling_desired_capacity():
    asg = COMPUTE_TF.split('resource "aws_autoscaling_group" "etl"', 1)[1]
    asg = asg.split('resource "aws_autoscaling_policy" "etl_cpu"', 1)[0]

    assert "desired_capacity    = 1" in asg
    assert "lifecycle {" in asg
    assert "ignore_changes = [desired_capacity]" in asg


def test_autoscaling_bounds_remain_managed_by_terraform():
    assert 'min_size            = var.environment == "prod" ? 1 : 0' in COMPUTE_TF
    assert 'max_size            = var.environment == "prod" ? 4 : 2' in COMPUTE_TF
    assert 'predefined_metric_type = "ASGAverageCPUUtilization"' in COMPUTE_TF
    assert "target_value = 60" in COMPUTE_TF
