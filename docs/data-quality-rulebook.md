# Data Quality Rulebook

## Purpose

This rulebook governs how synthetic ride-booking records move from raw input to analytics-ready output.

## Immutable raw zone

Raw files are never overwritten. Each processing run must produce a profile, cleaned output, rejected/quarantined records, and a reconciliation summary.

## Null policy

| Condition | Treatment |
|---|---|
| Missing booking ID or booking status | Quarantine |
| Expected field absence on a cancelled ride | Preserve null |
| Missing financial field on a successful ride | Flag and exclude from completed revenue |
| Missing non-critical category | Use `Unknown` only after preserving a quality flag |
| Missing ratings/TAT | Do not impute with zero or an average |

## Duplicate policy

| Condition | Treatment |
|---|---|
| Exact duplicate row | Retain first row, mark later row as removed duplicate |
| Same booking ID and same business data | Retain one deterministic row and record the event |
| Same booking ID with conflicting values | Quarantine all conflicting records for investigation |
| Similar rows with different booking IDs | Retain; they may be legitimate independent rides |

## Core validations

- `booking_id` must match `^CNR\\d{10}$`.
- Booking status must map to one governed value: `Success`, `Canceled by Customer`, `Canceled by Driver`, or `Driver Not Found`.
- Ratings must be in the 0–5 range.
- Fare, distance, and time values cannot be negative.
- A customer-cancelled ride requires a customer cancellation reason.
- A driver-cancelled ride requires a driver cancellation reason.
- An incomplete ride requires an incomplete-ride reason.
- Completed revenue is only eligible for successful, non-incomplete rides with a non-null booking value.

## Reconciliation

```text
raw rows = clean rows + flagged rows + quarantined rows + exact duplicates removed
```

The equality must hold for every pipeline run.
