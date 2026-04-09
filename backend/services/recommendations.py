"""
Recommendations Engine

Generates AI-driven skincare recommendations based on detected conditions.
Provides structured AM/PM routines and condition-specific advice.
"""


def generate_recommendations(analysis: dict) -> dict:
    """
    Generate personalized skincare recommendations.

    Args:
        analysis: Full analysis result from SkinAnalyzer

    Returns:
        dict with structured recommendations
    """
    severity = analysis.get("acne_severity", {})
    grade = severity.get("grade", "Clear")
    lesion_count = analysis.get("lesion_count", 0)
    inflammatory = severity.get("inflammatory_count", 0)
    comedonal = severity.get("comedonal_count", 0)
    pigmentation = analysis.get("hyperpigmentation", {})
    pig_coverage = pigmentation.get("coverage_pct", 0)
    zones = analysis.get("zone_health", {})

    recommendations = {
        "summary": _get_summary(grade, lesion_count, pig_coverage),
        "am_routine": _get_am_routine(grade, pig_coverage),
        "pm_routine": _get_pm_routine(grade, inflammatory, comedonal, pig_coverage),
        "key_ingredients": _get_key_ingredients(grade, inflammatory, pig_coverage),
        "lifestyle": _get_lifestyle_tips(grade, zones),
        "warnings": _get_warnings(grade, inflammatory),
        "confidence_note": "This is an AI-generated, non-diagnostic screening. Always consult a dermatologist for medical advice.",
    }

    return recommendations


def _get_summary(grade: str, lesion_count: int, pig_coverage: float) -> str:
    """Generate analysis summary."""
    summaries = {
        "Clear": f"Your skin appears healthy with no significant lesions detected. "
                 f"Hyperpigmentation coverage is at {pig_coverage}%. Focus on maintaining your current routine.",
        "Mild": f"Mild acne detected with {lesion_count} lesion(s). "
                f"Pigmentation at {pig_coverage}%. A targeted routine can help clear this up within 4-6 weeks.",
        "Moderate": f"Moderate acne detected with {lesion_count} lesion(s). "
                    f"Pigmentation at {pig_coverage}%. A consistent treatment routine is recommended.",
        "Severe": f"Significant acne detected with {lesion_count} lesion(s). "
                  f"Pigmentation at {pig_coverage}%. Professional dermatological consultation is strongly recommended.",
    }
    return summaries.get(grade, summaries["Clear"])


def _get_am_routine(grade: str, pig_coverage: float) -> list:
    """Generate morning routine steps."""
    routine = [
        {
            "step": 1,
            "action": "Gentle Cleanser",
            "detail": "Use a pH-balanced (5.5) gentle foaming cleanser. Avoid harsh surfactants like SLS.",
            "ingredients": ["Ceramides", "Glycerin", "Niacinamide"],
        },
    ]

    if grade in ["Moderate", "Severe"]:
        routine.append({
            "step": 2,
            "action": "Active Treatment",
            "detail": "Apply a lightweight salicylic acid (BHA) serum to prevent new breakouts.",
            "ingredients": ["Salicylic Acid 2%", "Zinc PCA"],
        })
    
    if pig_coverage > 10:
        routine.append({
            "step": len(routine) + 1,
            "action": "Vitamin C Serum",
            "detail": "Apply a stabilized Vitamin C serum (10-15%) to brighten and reduce dark spots.",
            "ingredients": ["L-Ascorbic Acid", "Ferulic Acid", "Vitamin E"],
        })

    routine.append({
        "step": len(routine) + 1,
        "action": "Lightweight Moisturizer",
        "detail": "Apply an oil-free, non-comedogenic moisturizer to maintain skin barrier.",
        "ingredients": ["Hyaluronic Acid", "Squalane", "Centella Asiatica"],
    })

    routine.append({
        "step": len(routine) + 1,
        "action": "Broad Spectrum SPF 50+",
        "detail": "Essential — UV exposure worsens pigmentation and acne scars. Reapply every 2 hours.",
        "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Niacinamide"],
    })

    return routine


def _get_pm_routine(grade: str, inflammatory: int, comedonal: int, pig_coverage: float) -> list:
    """Generate evening routine steps."""
    routine = [
        {
            "step": 1,
            "action": "Double Cleanse",
            "detail": "Start with an oil-based cleanser to remove SPF/makeup, followed by a water-based gel cleanser.",
            "ingredients": ["Jojoba Oil", "Micellar Water"],
        },
    ]

    if grade == "Mild":
        routine.append({
            "step": 2,
            "action": "Niacinamide Serum",
            "detail": "Apply 10% Niacinamide serum to control sebum, reduce redness, and minimize pores.",
            "ingredients": ["Niacinamide 10%", "Zinc 1%"],
        })
    elif grade in ["Moderate", "Severe"]:
        routine.append({
            "step": 2,
            "action": "Retinoid Treatment",
            "detail": "Apply a gentle retinoid (start 2-3x/week, build tolerance). This promotes cell turnover and prevents clogged pores.",
            "ingredients": ["Adapalene 0.1%", "Retinol 0.3%", "Bakuchiol (natural alternative)"],
        })

    if inflammatory > 3:
        routine.append({
            "step": len(routine) + 1,
            "action": "Anti-Inflammatory Spot Treatment",
            "detail": "Dab benzoyl peroxide (2.5%) on active inflamed lesions. The lower concentration reduces irritation while maintaining efficacy.",
            "ingredients": ["Benzoyl Peroxide 2.5%", "Tea Tree Oil"],
        })

    if pig_coverage > 15:
        routine.append({
            "step": len(routine) + 1,
            "action": "Brightening Treatment",
            "detail": "Apply an alpha arbutin or tranexamic acid serum to target stubborn dark spots.",
            "ingredients": ["Alpha Arbutin 2%", "Tranexamic Acid", "Kojic Acid"],
        })

    routine.append({
        "step": len(routine) + 1,
        "action": "Rich Night Moisturizer",
        "detail": "Seal in treatments with a rich, barrier-repairing night cream.",
        "ingredients": ["Ceramides", "Peptides", "Shea Butter"],
    })

    return routine


def _get_key_ingredients(grade: str, inflammatory: int, pig_coverage: float) -> list:
    """Get prioritized key ingredients based on conditions."""
    ingredients = []

    if grade in ["Moderate", "Severe"]:
        ingredients.extend([
            {"name": "Salicylic Acid (BHA)", "purpose": "Unclogs pores, reduces comedones", "priority": "high"},
            {"name": "Benzoyl Peroxide", "purpose": "Kills acne-causing bacteria", "priority": "high"},
        ])

    if inflammatory > 2:
        ingredients.extend([
            {"name": "Niacinamide", "purpose": "Reduces inflammation and redness", "priority": "high"},
            {"name": "Centella Asiatica", "purpose": "Soothes irritation, promotes healing", "priority": "medium"},
        ])

    if pig_coverage > 10:
        ingredients.extend([
            {"name": "Vitamin C", "purpose": "Brightens skin, fades dark spots", "priority": "high"},
            {"name": "Alpha Arbutin", "purpose": "Inhibits melanin production", "priority": "medium"},
            {"name": "SPF 50+", "purpose": "Prevents further pigmentation", "priority": "critical"},
        ])

    if grade == "Mild" or not ingredients:
        ingredients.extend([
            {"name": "Hyaluronic Acid", "purpose": "Deep hydration and plumping", "priority": "medium"},
            {"name": "Ceramides", "purpose": "Strengthens skin barrier", "priority": "medium"},
        ])

    return ingredients


def _get_lifestyle_tips(grade: str, zones: dict) -> list:
    """Generate lifestyle recommendations."""
    tips = [
        "Drink at least 8 glasses of water daily for skin hydration",
        "Change pillowcases every 2-3 days to reduce bacteria exposure",
        "Avoid touching your face throughout the day",
    ]

    if grade in ["Moderate", "Severe"]:
        tips.extend([
            "Reduce dairy and high-glycemic foods which can trigger breakouts",
            "Manage stress through exercise or meditation — cortisol worsens acne",
            "Aim for 7-9 hours of sleep for optimal skin repair",
        ])

    # Zone-specific tips
    chin_zone = zones.get("chin_jawline", {})
    if chin_zone.get("affected"):
        tips.append("Chin/jawline acne may be hormonal — consider consulting an endocrinologist")

    forehead_zone = zones.get("forehead", {})
    if forehead_zone.get("affected"):
        tips.append("Forehead breakouts may be linked to hair products — try keeping hair off your forehead")

    return tips


def _get_warnings(grade: str, inflammatory: int) -> list:
    """Generate important warnings."""
    warnings = []

    if grade == "Severe":
        warnings.append(
            "⚠️ Severe acne detected — professional dermatological evaluation is strongly recommended. "
            "Prescription treatments like isotretinoin may be necessary."
        )

    if inflammatory > 10:
        warnings.append(
            "⚠️ High number of inflammatory lesions — do NOT squeeze or pop these. "
            "This can lead to scarring and spread of infection."
        )

    warnings.append(
        "ℹ️ This is an AI-powered screening tool and does NOT constitute medical diagnosis. "
        "Results should be discussed with a qualified dermatologist."
    )

    return warnings
