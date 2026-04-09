"""
Progress Tracking Service

Generates simulated projections for skin health improvement:
- Now: Current detected conditions
- Short Term (4-6 weeks): Projected improvement with treatment
- Long Term (3-6 months): Projected clear state
"""


def generate_progress(analysis: dict) -> dict:
    """
    Generate three-stage progress projections.

    Args:
        analysis: Full analysis result from SkinAnalyzer

    Returns:
        dict with 'now', 'short_term', 'long_term' stages
    """
    severity = analysis.get("acne_severity", {})
    grade = severity.get("grade", "Clear")
    lesion_count = analysis.get("lesion_count", 0)
    inflammatory = severity.get("inflammatory_count", 0)
    comedonal = severity.get("comedonal_count", 0)
    pig = analysis.get("hyperpigmentation", {})
    pig_pct = pig.get("coverage_pct", 0)
    zones = analysis.get("zone_health", {})

    affected_zones = [z for z, info in zones.items() if info.get("affected")]

    return {
        "now": _stage_now(grade, lesion_count, inflammatory, comedonal, pig_pct, affected_zones),
        "short_term": _stage_short_term(grade, lesion_count, inflammatory, pig_pct, affected_zones),
        "long_term": _stage_long_term(grade, lesion_count, pig_pct),
    }


def _stage_now(grade, lesion_count, inflammatory, comedonal, pig_pct, affected_zones):
    """Current condition stage."""
    conditions = []

    if grade == "Clear":
        conditions.append("✅ Skin appears clear with no significant acne")
    else:
        conditions.append(f"🔴 Acne severity: {grade}")
        conditions.append(f"📊 {lesion_count} active lesion(s) detected")
        if inflammatory > 0:
            conditions.append(f"🔥 {inflammatory} inflammatory lesion(s) — red, swollen bumps")
        if comedonal > 0:
            conditions.append(f"⚪ {comedonal} comedonal lesion(s) — blackheads/whiteheads")

    if pig_pct > 5:
        conditions.append(f"🟤 Hyperpigmentation: {pig_pct}% coverage")
    else:
        conditions.append(f"✅ Minimal hyperpigmentation ({pig_pct}%)")

    if affected_zones:
        zone_str = ", ".join(z.replace("_", " ").title() for z in affected_zones)
        conditions.append(f"📍 Affected zones: {zone_str}")

    return {
        "label": "Now",
        "subtitle": "Current Condition",
        "timeframe": "Today",
        "severity": grade,
        "conditions": conditions,
        "metrics": {
            "acne_grade": grade,
            "lesion_count": lesion_count,
            "pigmentation_pct": pig_pct,
        },
    }


def _stage_short_term(grade, lesion_count, inflammatory, pig_pct, affected_zones):
    """Short-term projected improvement (4-6 weeks)."""
    conditions = []

    # Project improvement
    if grade == "Clear":
        projected_grade = "Clear"
        conditions.append("✅ Maintain clear skin with consistent routine")
    elif grade == "Mild":
        projected_grade = "Clear"
        conditions.append("✅ Most mild breakouts resolved")
        conditions.append("📉 Reduced active lesions by ~80%")
    elif grade == "Moderate":
        projected_grade = "Mild"
        conditions.append("📉 Acne improving: Moderate → Mild")
        conditions.append(f"📊 Active lesions reduced to ~{max(1, lesion_count // 3)}")
        conditions.append("🔥 Inflammatory lesions significantly reduced")
    else:
        projected_grade = "Moderate"
        conditions.append("📉 Acne improving: Severe → Moderate")
        conditions.append(f"📊 Active lesions reduced to ~{max(3, lesion_count // 2)}")
        conditions.append("⚠️ Some inflammatory lesions may persist — continue treatment")

    if pig_pct > 10:
        new_pct = round(pig_pct * 0.7, 1)
        conditions.append(f"🟤 Pigmentation reducing: {pig_pct}% → ~{new_pct}%")
    elif pig_pct > 5:
        conditions.append("🟤 Dark spots beginning to fade with consistent SPF use")

    conditions.append("✨ Visible improvement in skin texture and smoothness")
    conditions.append("🛡️ Stronger skin barrier from consistent moisturizing")

    return {
        "label": "Short Term",
        "subtitle": "4-6 Week Projection",
        "timeframe": "4-6 weeks",
        "severity": projected_grade,
        "conditions": conditions,
        "metrics": {
            "acne_grade": projected_grade,
            "lesion_count": max(0, lesion_count // 3),
            "pigmentation_pct": round(pig_pct * 0.7, 1),
        },
    }


def _stage_long_term(grade, lesion_count, pig_pct):
    """Long-term projected state (3-6 months)."""
    conditions = []

    if grade == "Clear":
        projected_grade = "Clear"
        conditions.append("✅ Consistently clear, healthy skin")
        conditions.append("🌟 Skin barrier fully optimized")
    elif grade in ["Mild", "Moderate"]:
        projected_grade = "Clear"
        conditions.append("✅ Breakouts fully cleared")
        conditions.append("🌟 Smooth, even-toned skin achieved")
        conditions.append("📉 Active lesions reduced to 0-1")
    else:
        projected_grade = "Mild"
        conditions.append("📉 Significant improvement: Severe → Mild")
        conditions.append(f"📊 Lesions reduced from {lesion_count} to ~{max(1, lesion_count // 5)}")
        conditions.append("💊 Consider ongoing maintenance with dermatologist guidance")

    if pig_pct > 15:
        new_pct = round(pig_pct * 0.3, 1)
        conditions.append(f"🟤 Pigmentation greatly reduced: {pig_pct}% → ~{new_pct}%")
    elif pig_pct > 5:
        conditions.append("✅ Dark spots significantly faded")
    else:
        conditions.append("✅ Even skin tone maintained")

    conditions.append("✨ Refined pores and improved skin texture")
    conditions.append("🛡️ Resilient skin barrier with consistent care")

    return {
        "label": "Long Term",
        "subtitle": "3-6 Month Projection",
        "timeframe": "3-6 months",
        "severity": projected_grade,
        "conditions": conditions,
        "metrics": {
            "acne_grade": projected_grade,
            "lesion_count": max(0, lesion_count // 5),
            "pigmentation_pct": round(pig_pct * 0.3, 1),
        },
    }
