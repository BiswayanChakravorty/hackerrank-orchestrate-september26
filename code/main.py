"""Command-line entry point for the Buy or Wait deterministic solution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from buy_or_wait import BaselineSimulator, CashFlowNormalizer, DatasetLoader, DatasetValidationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Buy or Wait input validation")
    parser.add_argument("--validate-input", action="store_true", help="validate dataset inputs without generating output.csv")
    parser.add_argument("--simulate-baseline", action="store_true", help="run deterministic baseline simulations without generating output.csv")
    parser.add_argument("--dataset-dir", type=Path, default=Path(__file__).resolve().parents[1] / "dataset")
    args = parser.parse_args()
    if not args.validate_input and not args.simulate_baseline:
        parser.error("use --validate-input or --simulate-baseline; decision generation is intentionally not available yet")
    try:
        dataset = DatasetLoader(args.dataset_dir).load()
    except DatasetValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Dataset validation passed: {args.dataset_dir}")
    for filename, count in dataset.row_counts().items():
        print(f"  {filename}: {count} rows")
    print(f"  image-backed event amounts resolved: {sum(event.amount_from_image_evidence for event in dataset.events)}")
    print("No output.csv was generated.")
    if args.simulate_baseline:
        simulator = BaselineSimulator(CashFlowNormalizer(dataset))
        results = tuple(simulator.simulate(request) for request in dataset.requests)
        repeated = tuple(simulator.simulate(request) for request in dataset.requests)
        if results != repeated:
            print("Baseline simulation is not repeatable.", file=sys.stderr)
            return 1
        violations = sum(result.violates_minimum_balance for result in results)
        print(f"Baseline simulations completed: {len(results)} requests; minimum-balance violations: {violations}; repeatability: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
