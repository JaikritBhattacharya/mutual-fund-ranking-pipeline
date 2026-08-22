"""Pure functions for eligibility screening and category-relative ranking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class Fund:
    """Minimal research record required by the ranking methodology."""

    name: str
    category: str
    plan_type: str
    geography: str
    fund_house_aum_crore: float | None
    track_record_years: float | None
    rolling_return: float | None
    sharpe_ratio: float | None


@dataclass(frozen=True)
class RankingConfig:
    """Explicit eligibility thresholds and score weights."""

    min_fund_house_aum_crore: float = 25_000.0
    min_track_record_years: float = 5.0
    rolling_weight: float = 0.80
    sharpe_weight: float = 0.20
    domestic_only: bool = True
    domestic_label: str = "India"

    def __post_init__(self) -> None:
        if self.min_fund_house_aum_crore < 0 or self.min_track_record_years < 0:
            raise ValueError("Eligibility thresholds cannot be negative")
        if self.rolling_weight < 0 or self.sharpe_weight < 0:
            raise ValueError("Score weights cannot be negative")
        if abs(self.rolling_weight + self.sharpe_weight - 1.0) > 1e-12:
            raise ValueError("Score weights must sum to 1.0")


@dataclass(frozen=True)
class RankedFund:
    """A screened fund with peer-relative component scores."""

    fund: Fund
    rank: int
    peer_count: int
    rolling_score: float
    sharpe_score: float
    final_score: float

    def as_dict(self) -> dict[str, object]:
        return {
            **asdict(self.fund),
            "rank": self.rank,
            "peer_count": self.peer_count,
            "rolling_score": self.rolling_score,
            "sharpe_score": self.sharpe_score,
            "final_score": self.final_score,
        }


def _finite(value: float | None) -> bool:
    return value is not None and isfinite(float(value))


def exclusion_reasons(fund: Fund, config: RankingConfig) -> tuple[str, ...]:
    """Return every failed rule rather than stopping at the first failure."""

    reasons: list[str] = []
    if config.domestic_only and fund.geography.casefold() != config.domestic_label.casefold():
        reasons.append("non-domestic geography")
    if not _finite(fund.fund_house_aum_crore):
        reasons.append("missing fund-house AUM")
    elif float(fund.fund_house_aum_crore) < config.min_fund_house_aum_crore:
        reasons.append("fund-house AUM below minimum")
    if not _finite(fund.track_record_years):
        reasons.append("missing track record")
    elif float(fund.track_record_years) < config.min_track_record_years:
        reasons.append("track record below minimum")
    if not _finite(fund.rolling_return):
        reasons.append("missing rolling return")
    if not _finite(fund.sharpe_ratio):
        reasons.append("missing Sharpe ratio")
    return tuple(reasons)


def percentile_score(value: float, peer_values: Iterable[float]) -> float:
    """Return a 0–100 midrank percentile score within a peer group."""

    values = [float(item) for item in peer_values if isfinite(float(item))]
    if not values:
        raise ValueError("At least one finite peer value is required")
    if len(values) == 1:
        return 100.0

    numeric = float(value)
    lower = sum(item < numeric for item in values)
    equal = sum(item == numeric for item in values)
    return 100.0 * (lower + (equal - 1) / 2) / (len(values) - 1)


def rank_universe(
    funds: Iterable[Fund], config: RankingConfig | None = None
) -> tuple[list[RankedFund], dict[str, tuple[str, ...]]]:
    """Screen a universe, rank eligible funds by category, and return an audit."""

    active_config = config or RankingConfig()
    eligible_by_category: dict[str, list[Fund]] = {}
    exclusions: dict[str, tuple[str, ...]] = {}

    for fund in funds:
        reasons = exclusion_reasons(fund, active_config)
        if reasons:
            exclusions[fund.name] = reasons
        else:
            eligible_by_category.setdefault(fund.category, []).append(fund)

    results: list[RankedFund] = []
    for category in sorted(eligible_by_category):
        peers = eligible_by_category[category]
        rolling_values = [float(fund.rolling_return) for fund in peers]
        sharpe_values = [float(fund.sharpe_ratio) for fund in peers]
        scored: list[tuple[Fund, float, float, float]] = []

        for fund in peers:
            rolling_score = percentile_score(float(fund.rolling_return), rolling_values)
            sharpe_score = percentile_score(float(fund.sharpe_ratio), sharpe_values)
            final_score = (
                active_config.rolling_weight * rolling_score
                + active_config.sharpe_weight * sharpe_score
            )
            scored.append((fund, rolling_score, sharpe_score, final_score))

        scored.sort(
            key=lambda item: (
                -item[3],
                -float(item[0].rolling_return),
                -float(item[0].sharpe_ratio),
                item[0].name.casefold(),
            )
        )
        results.extend(
            RankedFund(
                fund=fund,
                rank=index,
                peer_count=len(scored),
                rolling_score=round(rolling_score, 2),
                sharpe_score=round(sharpe_score, 2),
                final_score=round(final_score, 2),
            )
            for index, (fund, rolling_score, sharpe_score, final_score) in enumerate(
                scored, start=1
            )
        )

    return results, exclusions
