# Mutual Fund Ranking Pipeline

[![Tests](https://github.com/JaikritBhattacharya/mutual-fund-ranking-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/JaikritBhattacharya/mutual-fund-ranking-pipeline/actions/workflows/tests.yml)

This started as part of a larger fund-finder idea. I pulled out the quantitative core that I could publish safely: screening funds, comparing them with the right peers, combining return and risk measures, and keeping track of exclusions.

The data in this repo are synthetic. This is not investment advice or a list of recommended funds.

## How the ranking works

A fund has to pass the screen before it receives a score:

- domestic geography, when that filter is on;
- minimum fund-house AUM;
- minimum track record;
- available rolling-return and Sharpe-ratio values.

Eligible funds are compared only with funds in the same category.

```text
rolling_score = percentile_rank(rolling_return)
sharpe_score  = percentile_rank(sharpe_ratio)
final_score   = 0.80 × rolling_score + 0.20 × sharpe_score
```

The weights are configurable. Ties use a midrank rule.

## Why I built it this way

Mixing raw return percentages with raw Sharpe ratios would make the weights hard to interpret. Converting both to 0–100 peer scores puts them on the same scale.

I also keep excluded funds separate with the reason each one failed. That makes it possible to tell whether a fund ranked poorly or never qualified in the first place.

## Run it

Requires Python 3.10 or newer.

```bash
PYTHONPATH=src python3 -m fund_ranking examples/funds.csv
python3 -m unittest discover -s tests -v
```

The command prints JSON with the ranking and exclusion list.

## Files

```text
src/fund_ranking/engine.py   screening, peer scores, and ranking
src/fund_ranking/__main__.py CSV command-line interface
examples/funds.csv           synthetic fund universe
tests/test_engine.py         tests for thresholds, ties, weights, and peer groups
```

## What is not public

I left out production caches, live recommendations, investor information, internal product notes, service code, and credentials.

A serious research version would still need point-in-time source snapshots, survivorship-bias controls, benchmark-relative measures, transaction costs, and walk-forward testing.
