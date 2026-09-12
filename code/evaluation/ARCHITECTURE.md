# Deterministic Buy-or-Wait architecture

`DatasetLoader` validates and types the participant-facing CSV files.  Reviewed
image amounts and the narrow deterministic evidence amendment parser feed
`CashFlowNormalizer`, which applies status, settlement-date, FX, duplicate, and
exact-recurrence rules.  `BaselineSimulator` owns daily Decimal balance safety.

`BaselineAffordabilityCalculator` computes baseline capacity independently of
payment preferences.  `DeterministicPlanner` then constructs only full-payment,
partial-payment, and provider-supplied installment schedules, verifies each
against the same simulated trajectory, and ranks eligible schedules according
to deadline, changes, cost, start date, count, and option ID.  No LLM is used:
messages are untrusted and only the deterministic amendment parser can create a
validated financial amendment.

`output.write_output` validates the exact schema and request-ID set before
writing the root `output.csv`.  Any malformed row or nondeterministic second
run fails closed.
