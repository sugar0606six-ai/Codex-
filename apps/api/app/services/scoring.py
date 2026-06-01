from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreInput:
    demand: float
    margin: float
    competition: float
    catalog_match: float
    risk: float


def clamp(value: float, lower: float = 0, upper: float = 100) -> float:
    return max(lower, min(upper, value))


def opportunity_score(data: ScoreInput) -> float:
    demand = clamp(data.demand) / 100
    margin = clamp(data.margin) / 100
    competition = clamp(data.competition) / 100
    catalog = clamp(data.catalog_match) / 100
    risk_adjustment = 1 - (clamp(data.risk) / 120)
    return round(clamp(demand * margin * competition * catalog * risk_adjustment * 100), 2)


def decision(score: float, risk: float, margin_rate: float | None = None) -> str:
    if risk >= 70:
        return "放弃"
    if margin_rate is not None and margin_rate < 0.35:
        return "继续研究"
    if score >= 90:
        return "上架"
    if score >= 80:
        return "上架"
    if score >= 70:
        return "继续研究"
    return "放弃"


def risk_level(score: float) -> str:
    if score >= 70:
        return "高"
    if score >= 40:
        return "中"
    return "低"


def margin_score_from_rate(rate: float | None) -> float:
    if rate is None:
        return 35
    if rate >= 0.45:
        return 90
    if rate >= 0.35:
        return 70
    if rate >= 0.25:
        return 50
    return 25
