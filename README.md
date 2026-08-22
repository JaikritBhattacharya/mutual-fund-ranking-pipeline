# Mutual Fund Ranking Pipeline

[![Tests](https://github.com/jbhattac2323/mutual-fund-ranking-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/jbhattac2323/mutual-fund-ranking-pipeline/actions/workflows/tests.yml)

A privacy-safe, reproducible case study of an advisor-facing mutual-fund screening engine. The project turns a peer universe into an auditable shortlist using explicit eligibility rules, within-category normalization, and configurable risk-adjusted scoring.

> Educational methodology demonstrator only. It is not investment advice and does not recommend any real fund.

## Why this belongs in a quantitative portfolio

- Separates universe construction from ranking to reduce selection bias.
- Compares funds only with like-for-like category peers.
- Uses percentile ranks so return and Sharpe metrics share a common 0–100 scale.
- Produces both ranked results and exclusion reasons for auditability.
- Includes deterministic tests for thresholds, ties, peer groups, and weight validation.
- Uses only Python's standard library, so the example is easy to reproduce.
- Runs the methodology test suite across supported Python versions in GitHub Actions.

## Methodology

Each fund must pass the configured screen before it is ranked:

- domestic geography, when enabled;
- minimum fund-house assets under management;
- minimum track record;
- available rolling-return and Sharpe-ratio observations.

Eligible funds are grouped by category. Within each category:

```text
rolling_score = percentile_rank(rolling_return)
sharpe_score  = percentile_rank(sharpe_ratio)
final_score   = 0.80 × rolling_score + 0.20 × sharpe_score
```

Ties use a midrank convention. The default 80/20 weights are parameters rather than hidden constants.

For a production research system, the rolling-return input would be computed from historical NAV observations—for example, the median annualized return across overlapping three-year windows—and Sharpe would use a documented return frequency and risk-free-rate series.

## Run the synthetic example

Requires Python 3.10 or newer.

```bash
PYTHONPATH=src python3 -m fund_ranking examples/funds.csv
python3 -m unittest discover -s tests -v
```

The CLI prints JSON containing ranked funds and a separate exclusion audit. The example names and observations are synthetic.

## Repository map

```text
src/fund_ranking/engine.py   eligibility, normalization, and ranking
src/fund_ranking/__main__.py CSV-to-JSON command-line interface
examples/funds.csv           synthetic peer universe
tests/test_engine.py         deterministic methodology tests
```

## Data and governance boundary

This public case study deliberately excludes production caches, investor records, internal product documents, service code, credentials, and live recommendations. A real deployment should add source snapshots, as-of dates, survivorship-bias controls, benchmark-relative metrics, transaction-cost assumptions, and scheduled data-quality checks.

## Research extensions

- Walk-forward validation and ranking stability through time
- Bootstrap confidence intervals for rolling-return estimates
- Multiple-testing and selection-bias diagnostics
- Downside-risk measures such as Sortino ratio and maximum drawdown
- Benchmark- and category-relative attribution
- Missing-data and stale-NAV monitoring
