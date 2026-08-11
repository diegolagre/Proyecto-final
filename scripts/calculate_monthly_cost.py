#!/usr/bin/env python3
"""Calculate the documented AWS estimate from versioned assumptions."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


DEFAULT_INPUT = Path(__file__).parents[1] / "costs" / "aws-us-east-1.json"


def money(value: Decimal) -> str:
    return f"USD {value.quantize(Decimal('0.01')):,.2f}"


def calculate(items: list[dict]) -> tuple[list[tuple[str, Decimal]], Decimal]:
    categories: dict[str, Decimal] = defaultdict(Decimal)
    total = Decimal("0")
    for item in items:
        cost = Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"]))
        categories[item["category"]] += cost
        total += cost
    return sorted(categories.items()), total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    estimate = json.loads(args.input.read_text(encoding="utf-8"))

    monthly_categories, monthly_total = calculate(estimate["monthly_items"])
    one_time_categories, one_time_total = calculate(estimate["one_time_items"])

    print(f"Scenario: {estimate['scenario']} ({estimate['region']})")
    print("Monthly estimate")
    for category, value in monthly_categories:
        print(f"  {category:20} {money(value)}")
    print(f"  {'TOTAL':20} {money(monthly_total)}")
    print("One-time migration estimate")
    for category, value in one_time_categories:
        print(f"  {category:20} {money(value)}")
    print(f"  {'TOTAL':20} {money(one_time_total)}")


if __name__ == "__main__":
    main()
