"""Fail-closed submission schema validation and deterministic CSV writing."""
from __future__ import annotations
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

COLUMNS=("request_id","amount_safe_to_pay","affordability_status","recommended_payment_method","payment_plan","earliest_date_for_full_payment","spending_changes_needed","decision_explanation")

def validate_rows(rows: list[dict[str,str]], request_ids: tuple[str,...]) -> None:
    if len(rows)!=len(request_ids) or {r["request_id"] for r in rows} != set(request_ids) or len({r["request_id"] for r in rows}) != len(rows): raise ValueError("output rows must exactly match requests")
    for row in rows:
        if tuple(row) != COLUMNS: raise ValueError("output columns are invalid")
        try:
            if Decimal(row["amount_safe_to_pay"]) < 0: raise ValueError
        except (InvalidOperation, ValueError): raise ValueError("invalid safe amount")
        if row["affordability_status"] not in {"affordable_now","affordable_with_plan","affordable_later","not_affordable"}: raise ValueError("invalid status")
        if row["recommended_payment_method"] not in {"full_payment","partial_payment","installments","wait","not_recommended"}: raise ValueError("invalid method")
        if row["earliest_date_for_full_payment"]: date.fromisoformat(row["earliest_date_for_full_payment"])
        if row["payment_plan"] == "none" and row["recommended_payment_method"] != "not_recommended": raise ValueError("accepted plan is missing")

def write_output(path: Path, rows: list[dict[str,str]], request_ids: tuple[str,...]) -> None:
    validate_rows(rows, request_ids)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=COLUMNS); writer.writeheader(); writer.writerows(rows)
