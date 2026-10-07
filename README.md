# Ola RideOps Intelligence Platform

A production-style mobility analytics portfolio project that transforms synthetic ride-booking data into governed, testable operational intelligence.

> **Build date:** 07 October 2026  
> **Dataset period:** July 2024  
> **Dataset notice:** This repository uses synthetic educational data only. It is not affiliated with Ola and contains no real customer, driver, or operational data.

## What this project demonstrates

- Data ingestion, profiling, standardisation, and quarantine-based cleaning
- Explicit handling of nulls, exact duplicates, invalid booking IDs, and invalid booking statuses
- PostgreSQL staging/core modelling and SQL-ready analytics layers
- Testable Python code with `pytest`
- Local application and database orchestration with Docker Compose
- CI automation with GitHub Actions

## Architecture

```text
Raw CSV -> staging -> validation and quarantine -> cleaned core bookings
       -> PostgreSQL analytics marts -> Streamlit / Power BI -> operational decisions
```

## Data-quality principles

1. Raw source data is immutable.
2. Critical errors are quarantined, never silently discarded.
3. Exact duplicate records are removed with an audit flag.
4. A booking ID must match `CNR` followed by 10 digits.
5. Revenue is computed only from eligible completed rides; it is never calculated by counting booking values.
6. A cancelled or driver-not-found ride is not completed revenue.

## Quick start

```bash
git clone https://github.com/AnyalstRushi/ola-rideops-intelligence.git
cd ola-rideops-intelligence
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

For containerised local services:

```bash
docker compose up --build
```

## Repository layout

```text
src/ola_rideops/   Python pipeline modules
tests/             Unit tests
sql/               PostgreSQL schema and analytics SQL
docs/              Business, quality, KPI, and architecture documentation
data/sample/       Small safe synthetic sample only
.github/workflows/ Continuous integration
```

## Roadmap

- [x] Repository foundation and quality-rule specification
- [x] Initial booking-ID/status standardisation tests
- [ ] Full CSV profile and reconciliation report
- [ ] Null, duplicate, and business-rule quarantine pipeline
- [ ] Postgres analytics marts and KPI reconciliation
- [ ] Streamlit dashboard
- [ ] Risk-scoring experiment and model card
- [ ] Client presentation and deployment runbook

## License

MIT License. See `LICENSE` when added.
