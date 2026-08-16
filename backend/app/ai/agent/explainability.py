"""Evidence-based candidate explanation and comparison from pipeline scores."""
from typing import Any, Dict, List, Optional


def _score(cand: Dict[str, Any], key: str, fallback_keys: Optional[List[str]] = None) -> float:
    if key in cand and cand[key] is not None:
        return float(cand[key])
    for alt in fallback_keys or []:
        if alt in cand and cand[alt] is not None:
            return float(cand[alt])
    components = cand.get("score_components") or {}
    if key in components:
        return float(components[key])
    return 0.0


def explain_candidate(cand: Dict[str, Any], rank_position: int = 1) -> Dict[str, Any]:
    """Build structured explanation from actual pipeline fields."""
    semantic = _score(cand, "cross_encoder_score", ["semantic_score"])
    skill = _score(cand, "skill_match_score")
    experience = _score(cand, "experience_score")
    behavioral = _score(cand, "behavioral_score", ["behavior_score"])
    final = _score(cand, "final_score")

    matched = cand.get("matched_skills") or []
    missing = cand.get("missing_skills") or []
    profile = cand.get("profile") or {}
    name = profile.get("name") or cand.get("name") or f"Candidate {str(cand.get('candidate_id', ''))[:8]}"
    email = profile.get("email") or cand.get("email")

    factors: List[str] = []
    if skill >= 80:
        factors.append("strong required skill coverage")
    if semantic >= 80:
        factors.append("high semantic relevance to the job description")
    if experience >= 80:
        factors.append("solid experience alignment")
    if behavioral >= 70:
        factors.append("positive behavioral signals")
    if not factors:
        factors.append("best available match among retrieved candidates")

    rank_reason = (
        f"Ranked #{rank_position}: strongest combination of "
        + ", ".join(factors[:2])
        + "."
    )

    return {
        "candidate_id": cand.get("candidate_id"),
        "name": name,
        "email": email,
        "rank_position": rank_position,
        "overall_score": round(final, 2),
        "skill_match_score": round(skill, 2),
        "semantic_relevance": round(semantic, 2),
        "experience_score": round(experience, 2),
        "behavioral_score": round(behavioral, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "ranking_factors": factors,
        "why_ranked": rank_reason,
        "flags": cand.get("flags") or [],
    }


def compare_candidates(candidates: List[Dict[str, Any]], top_n: int = 3) -> Dict[str, Any]:
    """Compare top-N candidates using real pipeline scores."""
    ranked = sorted(candidates, key=lambda c: _score(c, "final_score"), reverse=True)[:top_n]
    comparisons: List[Dict[str, Any]] = []
    for i, cand in enumerate(ranked, start=1):
        exp = explain_candidate(cand, rank_position=i)
        comparisons.append({
            "candidate_id": exp["candidate_id"],
            "name": exp["name"],
            "rank_position": i,
            "skill_match_score": exp["skill_match_score"],
            "semantic_relevance": exp["semantic_relevance"],
            "experience_score": exp["experience_score"],
            "behavioral_score": exp["behavioral_score"],
            "final_score": exp["overall_score"],
            "matched_skills": exp["matched_skills"],
            "missing_skills": exp["missing_skills"],
        })

    recommendation = ""
    if len(comparisons) >= 2:
        top = comparisons[0]
        second = comparisons[1]
        reasons: List[str] = []
        if top["skill_match_score"] > second["skill_match_score"]:
            reasons.append("stronger skill alignment")
        if top["semantic_relevance"] > second["semantic_relevance"]:
            reasons.append("higher semantic relevance")
        if not reasons:
            reasons.append("highest fused ranking score")
        competitive: List[str] = []
        if second["experience_score"] > top["experience_score"]:
            competitive.append(f"{second['name']} has stronger experience")
        if second["behavioral_score"] > top["behavioral_score"]:
            competitive.append(f"{second['name']} shows stronger behavioral signals")
        recommendation = (
            f"{top['name']} ranks highest due to {', '.join(reasons)}."
            + (f" {competitive[0]}." if competitive else "")
        )
    elif comparisons:
        recommendation = f"{comparisons[0]['name']} is the top ranked candidate based on pipeline scores."

    return {
        "candidates_compared": len(comparisons),
        "comparisons": comparisons,
        "recommendation": recommendation,
        "recommended_candidate_id": comparisons[0]["candidate_id"] if comparisons else None,
    }
