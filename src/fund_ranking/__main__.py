"""Run the ranking engine against a CSV universe and print auditable JSON."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .engine import Fund, rank_universe


def optional_float(value: str) -> float | None:
    stripped = value.strip()
    return float(stripped) if stripped else None


def load_funds(path: Path) -> list[Fund]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            Fund(
                name=row["name"],
                category=row["category"],
                plan_type=row["plan_type"],
                geography=row["geography"],
                fund_house_aum_crore=optional_float(row["fund_house_aum_crore"]),
                track_record_years=optional_float(row["track_record_years"]),
                rolling_return=optional_float(row["rolling_return"]),
                sharpe_ratio=optional_float(row["sharpe_ratio"]),
            )
            for row in rows
        ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    ranked, exclusions = rank_universe(load_funds(args.csv_path))
    output = {
        "ranked": [item.as_dict() for item in ranked],
        "exclusions": exclusions,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
