"""Deterministic daily baseline balance simulation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from .cashflows import CashFlowNormalizer
from .models import CashFlow, Request


@dataclass(frozen=True)
class BaselineSimulation:
    start_date: date
    end_date: date
    starting_balance: Decimal
    daily_balances: tuple[tuple[date, Decimal], ...]
    minimum_balance: Decimal
    minimum_balance_date: date
    normalized_cash_flows: tuple[CashFlow, ...]
    minimum_balance_to_keep: Decimal

    @property
    def violates_minimum_balance(self) -> bool:
        return self.minimum_balance < self.minimum_balance_to_keep


class BaselineSimulator:
    def __init__(self, normalizer: CashFlowNormalizer, *, horizon_days: int = 90) -> None:
        if horizon_days <= 0:
            raise ValueError("horizon_days must be positive")
        self.normalizer = normalizer
        self.horizon_days = horizon_days

    def simulate(self, request: Request) -> BaselineSimulation:
        profile = self.normalizer.profiles[request.user_id]
        flows = self.normalizer.normalize(request, horizon_days=self.horizon_days)
        flows_by_day: dict[date, list[CashFlow]] = {}
        for flow in flows:
            flows_by_day.setdefault(flow.flow_date, []).append(flow)
        balance = profile.current_available_balance
        minimum = balance
        minimum_date = request.request_date
        balances: list[tuple[date, Decimal]] = []
        for offset in range(self.horizon_days):
            current_date = request.request_date + timedelta(days=offset)
            # Stable provenance ordering makes same-day results reproducible.
            for flow in sorted(flows_by_day.get(current_date, ()), key=lambda item: (item.sequence, item.source_event_id or "")):
                if flow.direction == "credit":
                    balance += flow.amount
                elif flow.direction == "debit":
                    balance -= flow.amount
            balances.append((current_date, balance))
            if balance < minimum:
                minimum, minimum_date = balance, current_date
        return BaselineSimulation(request.request_date, request.request_date + timedelta(days=self.horizon_days - 1), profile.current_available_balance, tuple(balances), minimum, minimum_date, flows, profile.minimum_balance_to_keep)
