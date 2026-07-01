from dataclasses import dataclass


@dataclass
class GateResult:
    name: str
    status: str        # "Pass", "Fail", "Partial"
    score_cap: int     # 100 = no cap
    reason: str


def run_hard_gates(opportunity: dict, profile: dict) -> tuple[list[GateResult], int]:
    """
    Apply hard gates against an opportunity and company profile.
    Returns (list of gate results, effective score cap).
    Gates are caps not zeros — a failed gate surfaces the opportunity
    with a warning rather than hiding it.
    """
    gates = []
    cap = 100

    # Gate 1: Set-aside eligibility
    set_aside = (opportunity.get("SET_ASIDE") or "").lower()
    certifications = [c.lower() for c in profile.get("certifications", [])]

    if set_aside and set_aside not in ("", "none", "total small business set-aside"):
        eligible = _check_set_aside_eligibility(set_aside, certifications)
        if not eligible:
            gates.append(GateResult(
                name="eligibility",
                status="Fail",
                score_cap=40,
                reason=f"Set-aside '{set_aside}' requires certification company does not hold"
            ))
            cap = min(cap, 40)
        else:
            gates.append(GateResult(name="eligibility", status="Pass", score_cap=100, reason=""))
    else:
        gates.append(GateResult(name="eligibility", status="Pass", score_cap=100, reason="No set-aside restriction"))

    # Gate 2: Clearance
    required_clearance = (opportunity.get("DESCRIPTION") or "").lower()
    company_clearance = (profile.get("clearance") or "").lower()
    if "secret clearance" in required_clearance and "secret" not in company_clearance:
        gates.append(GateResult(
            name="clearance",
            status="Fail",
            score_cap=50,
            reason="Opportunity requires Secret clearance"
        ))
        cap = min(cap, 50)
    else:
        gates.append(GateResult(name="clearance", status="Pass", score_cap=100, reason=""))

    # Gate 3: Location (onsite-only)
    avoid = [a.lower() for a in profile.get("avoid", [])]
    description = (opportunity.get("DESCRIPTION") or "").lower()
    if "onsite" in avoid or "on-site" in avoid:
        if "on-site only" in description or "onsite only" in description:
            gates.append(GateResult(
                name="location",
                status="Fail",
                score_cap=60,
                reason="Opportunity requires onsite presence which company avoids"
            ))
            cap = min(cap, 60)
        else:
            gates.append(GateResult(name="location", status="Pass", score_cap=100, reason=""))
    else:
        gates.append(GateResult(name="location", status="Pass", score_cap=100, reason=""))

    # Gate 4: Contract size (10x above company max)
    max_executable = profile.get("max_contract_executable", 0)
    award_amount = opportunity.get("NAICS_MEDIAN_AWARD_AMOUNT") or 0
    if max_executable and award_amount > max_executable * 10:
        gates.append(GateResult(
            name="contract_size",
            status="Fail",
            score_cap=65,
            reason=f"Estimated award ${award_amount:,.0f} is 10x above company max ${max_executable:,.0f}"
        ))
        cap = min(cap, 65)
    else:
        gates.append(GateResult(name="contract_size", status="Pass", score_cap=100, reason=""))

    return gates, cap


def _check_set_aside_eligibility(set_aside: str, certifications: list[str]) -> bool:
    mapping = {
        "8(a)": ["8(a)", "8a"],
        "hubzone": ["hubzone"],
        "wosb": ["wosb", "women-owned"],
        "edwosb": ["edwosb", "wosb", "women-owned"],
        "sdvosb": ["sdvosb", "service-disabled veteran"],
        "vosb": ["vosb", "veteran-owned", "sdvosb"],
        "small business": ["small_business", "small business"],
        "total small business": ["small_business", "small business"],
    }
    for key, required in mapping.items():
        if key in set_aside:
            return any(c in certifications for c in required)
    return True  # unknown set-aside type — don't gate
