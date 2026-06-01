from app.services.scoring import ScoreInput, decision, opportunity_score


def test_high_risk_blocks_launch():
    score = opportunity_score(ScoreInput(demand=95, margin=90, competition=88, catalog_match=96, risk=82))
    assert score < 90
    assert decision(score, risk=82, margin_rate=0.5) == "放弃"


def test_balanced_candidate_can_launch():
    score = opportunity_score(ScoreInput(demand=92, margin=90, competition=86, catalog_match=95, risk=15))
    assert score >= 50
    assert decision(91, risk=15, margin_rate=0.46) == "上架"
