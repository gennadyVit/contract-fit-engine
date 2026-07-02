from dataclasses import dataclass
from api.scoring.rules_engine import run_hard_gates


WEIGHTS = {
    "capability_similarity": 0.35,
    "past_performance_match": 0.25,
    "contract_size_fit": 0.15,
    "competition_score": 0.15,
    "strategic_fit": 0.10,
}


@dataclass
class ScoreResult:
    notice_id: str
    title: str
    overall_fit_score: int
    confidence: str
    hard_gates: list
    components: dict
    agency_name: str
    naics_code: str
    days_until_deadline: int
    naics_median_award_amount: float
    naics_sb_win_rate_pct: float


def score_opportunity(opportunity: dict, profile: dict, capability_similarity: float = None) -> ScoreResult:
    """
    Score a single opportunity against a company profile.
    capability_similarity is injected from embeddings.py (Azure OpenAI).
    If None, stubbed to 0.5 until Azure is wired up.
    """
    gates, score_cap = run_hard_gates(opportunity, profile)

    components = {
        "capability_similarity": _score_capability_similarity(capability_similarity),
        "past_performance_match": _score_past_performance(opportunity, profile),
        "contract_size_fit": _score_contract_size(opportunity, profile),
        "competition_score": _score_competition(opportunity),
        "strategic_fit": _score_strategic_fit(opportunity, profile),
    }

    raw_score = sum(float(score) * WEIGHTS[name] for name, score in components.items())
    final_score = min(int(raw_score), score_cap)
    confidence = _compute_confidence(opportunity, profile, components)

    return ScoreResult(
        notice_id=opportunity.get("NOTICE_ID", ""),
        title=opportunity.get("TITLE", ""),
        overall_fit_score=final_score,
        confidence=confidence,
        hard_gates=[{"name": g.name, "status": g.status, "reason": g.reason} for g in gates],
        components={k: round(v) for k, v in components.items()},
        agency_name=opportunity.get("AGENCY_NAME", ""),
        naics_code=opportunity.get("NAICS_CODE", ""),
        days_until_deadline=opportunity.get("DAYS_UNTIL_DEADLINE") or 0,
        naics_median_award_amount=opportunity.get("NAICS_MEDIAN_AWARD_AMOUNT") or 0,
        naics_sb_win_rate_pct=opportunity.get("NAICS_SB_WIN_RATE_PCT") or 0,
    )


def _score_capability_similarity(similarity: float) -> float:
    """Stub returns 50 until Azure OpenAI embeddings are wired in."""
    if similarity is None:
        return 50.0
    return round(similarity * 100, 1)


def _score_past_performance(opportunity: dict, profile: dict) -> float:
    score = 0.0
    opp_text = (
        (opportunity.get("TITLE") or "") + " " +
        (opportunity.get("DESCRIPTION") or "")
    ).lower()

    keywords_target = [k.lower() for k in profile.get("keywords_target", [])]
    capabilities = [c.lower() for c in profile.get("capabilities", [])]
    all_terms = keywords_target + capabilities

    # keyword overlap with opportunity text
    matches = sum(1 for term in all_terms if term in opp_text)
    score += min(matches / max(len(all_terms), 1), 1.0) * 60

    # boost if past performance agency matches opportunity agency
    opp_agency = (opportunity.get("AGENCY_NAME") or "").lower()
    agency_prefs = [a.lower() for a in profile.get("agency_preferences", [])]
    if any(pref in opp_agency for pref in agency_prefs):
        score += 20

    # boost if past performance NAICS matches
    opp_naics = opportunity.get("NAICS_CODE", "")
    profile_naics = profile.get("naics", [])
    if opp_naics in profile_naics:
        score += 20

    return min(score, 100.0)


def _score_contract_size(opportunity: dict, profile: dict) -> float:
    pref = profile.get("preferred_contract_size", {})
    min_size = pref.get("min", 0)
    max_size = pref.get("max", float("inf"))
    median_amount = opportunity.get("NAICS_MEDIAN_AWARD_AMOUNT") or 0

    if median_amount == 0:
        return 50.0  # no data, neutral score

    if min_size <= median_amount <= max_size:
        return 100.0

    if median_amount < min_size:
        # below preferred min — decay proportionally
        ratio = median_amount / min_size
        return max(ratio * 100, 20.0)

    # above preferred max — decay proportionally
    ratio = max_size / median_amount
    return max(ratio * 100, 10.0)


def _score_competition(opportunity: dict) -> float:
    unique_vendors = opportunity.get("NAICS_UNIQUE_VENDORS") or 0

    if unique_vendors == 0:
        return 50.0  # no data, neutral

    # inverse of competition: fewer vendors = better score
    if unique_vendors <= 5:
        return 100.0
    elif unique_vendors <= 20:
        return 80.0
    elif unique_vendors <= 50:
        return 60.0
    elif unique_vendors <= 100:
        return 40.0
    else:
        return 20.0


def _score_strategic_fit(opportunity: dict, profile: dict) -> float:
    score = 0.0
    opp_text = (
        (opportunity.get("TITLE") or "") + " " +
        (opportunity.get("DESCRIPTION") or "")
    ).lower()

    # keyword target matches
    keywords_target = [k.lower() for k in profile.get("keywords_target", [])]
    target_hits = sum(1 for k in keywords_target if k in opp_text)
    score += min(target_hits / max(len(keywords_target), 1), 1.0) * 50

    # keyword avoid penalties
    keywords_avoid = [k.lower() for k in profile.get("keywords_avoid", [])]
    avoid_hits = sum(1 for k in keywords_avoid if k in opp_text)
    score -= avoid_hits * 15

    # agency preference boost
    opp_agency = (opportunity.get("AGENCY_NAME") or "").lower()
    agency_prefs = [a.lower() for a in profile.get("agency_preferences", [])]
    if any(pref in opp_agency for pref in agency_prefs):
        score += 30

    # small business set-aside boost
    set_aside = (opportunity.get("SET_ASIDE") or "").lower()
    if "small business" in set_aside or "8(a)" in set_aside:
        score += 20

    return max(min(score, 100.0), 0.0)


def _compute_confidence(opportunity: dict, profile: dict, components: dict) -> str:
    issues = 0

    # short or missing opportunity text
    opp_text = (opportunity.get("TITLE") or "") + (opportunity.get("DESCRIPTION") or "")
    if len(opp_text) < 100:
        issues += 1

    # vague company profile
    if len(profile.get("capabilities", [])) < 2:
        issues += 1

    # no award history for this NAICS
    if not opportunity.get("NAICS_MEDIAN_AWARD_AMOUNT"):
        issues += 1

    # capability similarity is stubbed
    if components.get("capability_similarity") == 50.0:
        issues += 1

    if issues == 0:
        return "High"
    elif issues <= 2:
        return "Medium"
    else:
        return "Low"
