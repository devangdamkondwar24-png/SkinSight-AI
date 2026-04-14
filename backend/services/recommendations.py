"""
Recommendations Engine

Generates AI-driven skincare recommendations based on detected conditions.
Provides structured AM/PM routines and condition-specific advice.
"""

# Product Library with Suitability Markers for Weighted Ranking
PRODUCT_LIBRARY = {
    "cleanser_bp": [
        {"brand": "Benzac AC", "name": "Benzoyl Peroxide Gel Wash", "benefit": "Clinically proven (India)", "intensity": 5, "focus": "inflammation", "skin_type": "oily"},
        {"brand": "PanOxyl", "name": "Acne Foaming Wash 10%", "benefit": "Maximum strength active", "intensity": 5, "focus": "inflammation", "skin_type": "oily"},
        {"brand": "PanOxyl", "name": "Acne Foaming Wash 4%", "benefit": "Balanced daily active", "intensity": 3, "focus": "inflammation", "skin_type": "all"},
        {"brand": "CeraVe", "name": "Acne Foaming Cream Cleanser", "benefit": "Calms while treating acne", "intensity": 2, "focus": "inflammation", "skin_type": "all"},
        {"brand": "Derma Co", "name": "1% Benzoyl Peroxide Face Wash", "benefit": "Gentle active for sensitivity", "intensity": 2, "focus": "inflammation", "skin_type": "all"}
    ],
    "cleanser_sa": [
        {"brand": "Minimalist", "name": "2% Salicylic Acid Cleanser", "benefit": "Pore decongestion (India)", "intensity": 3, "focus": "pores", "skin_type": "oily"},
        {"brand": "Saslic DS", "name": "Salicylic Acid Foaming Wash", "benefit": "Medical-grade clearing (India)", "intensity": 5, "focus": "pores", "skin_type": "oily"},
        {"brand": "Saslic", "name": "1% Salicylic Acid Foaming Wash", "benefit": "Mild pore clearing (India)", "intensity": 2, "focus": "pores", "skin_type": "all"},
        {"brand": "CeraVe", "name": "Renewing SA Cleanser", "benefit": "Smooths skin and clears pores", "intensity": 2, "focus": "pores", "skin_type": "all"},
        {"brand": "Re'equil", "name": "Fruit AHA Face Wash", "benefit": "Surface exfoliation (India)", "intensity": 2, "focus": "pigmentation", "skin_type": "all"}
    ],
    "cleanser_gentle": [
        {"brand": "Episoft AC", "name": "Cleansing Lotion", "benefit": "Prescribed for acne-prone skin", "intensity": 1, "focus": "barrier", "skin_type": "oily"},
        {"brand": "Cetaphil", "name": "Gentle Skin Cleanser", "benefit": "Soap-free hydration", "intensity": 1, "focus": "barrier", "skin_type": "dry"},
        {"brand": "Minimalist", "name": "Aquaporin Booster Cleanser", "benefit": "Deep hydration boost (India)", "intensity": 2, "focus": "barrier", "skin_type": "all"},
        {"brand": "Sebamed", "name": "Clear Face Foam", "benefit": "Maintains pH 5.5 (India)", "intensity": 2, "focus": "inflammation", "skin_type": "oily"},
        {"brand": "La Roche-Posay", "name": "Toleriane Hydrating Cleanser", "benefit": "Prebiotic thermal water", "intensity": 1, "focus": "barrier", "skin_type": "dry"}
    ],
    "serum_niacinamide": [
        {"brand": "Minimalist", "name": "10% Niacinamide Serum", "benefit": "Oil control and pore repair", "intensity": 4, "focus": "pores", "skin_type": "oily"},
        {"brand": "Minimalist", "name": "5% Niacinamide + HA", "benefit": "Gentle oil regulation", "intensity": 2, "focus": "barrier", "skin_type": "all"},
        {"brand": "Plum", "name": "10% Niacinamide Rice Water", "benefit": "Brightening (India)", "intensity": 3, "focus": "pigmentation", "skin_type": "all"},
        {"brand": "The Ordinary", "name": "Niacinamide 10% + Zinc 1%", "benefit": "High oil control", "intensity": 5, "focus": "pores", "skin_type": "oily"},
        {"brand": "The Derma Co", "name": "10% Niacinamide Serum", "benefit": "Reduces acne marks", "intensity": 4, "focus": "pigmentation", "skin_type": "all"}
    ],
    "ser_vitamin_c": [
        {"brand": "SkinCeuticals", "name": "C E Ferulic", "benefit": "Premium clinical antioxidant", "intensity": 5, "focus": "pigmentation", "skin_type": "all"},
        {"brand": "Minimalist", "name": "10% Vitamin C + AG", "benefit": "Stable brightening (India)", "intensity": 3, "focus": "pigmentation", "skin_type": "all"},
        {"brand": "Foxtale", "name": "C For Yourself Brightening", "benefit": "Instant glow (India)", "intensity": 2, "focus": "pigmentation", "skin_type": "all"},
        {"brand": "Plum", "name": "15% Vitamin C Mandarin", "benefit": "High potency dark spots", "intensity": 4, "focus": "pigmentation", "skin_type": "all"}
    ],
    "treatment_retinoid": [
        {"brand": "Aziderm", "name": "Azelaic Acid 20% Cream", "benefit": "Potent acne/spot treatment", "intensity": 5, "focus": "inflammation", "skin_type": "all"},
        {"brand": "Differin", "name": "Adapalene Gel 0.1%", "benefit": "Clinical acne treatment", "intensity": 5, "focus": "pores", "skin_type": "oily"},
        {"brand": "Minimalist", "name": "0.3% Retinol + Q10", "benefit": "Anti-aging & acne", "intensity": 3, "focus": "pores", "skin_type": "all"},
        {"brand": "Re'equil", "name": "0.1% Retinol Night Cream", "benefit": "Beginner friendly (India)", "intensity": 2, "focus": "barrier", "skin_type": "all"},
        {"brand": "The Ordinary", "name": "Retinol 0.5% in Squalane", "benefit": "Standard active", "intensity": 3, "focus": "pores", "skin_type": "dry"}
    ],
    "spf": [
        {"brand": "Re'equil", "name": "Ultra Matte Dry Touch SPF 50", "benefit": "Velvet finish for oily skin", "intensity": 5, "focus": "barrier", "skin_type": "oily"},
        {"brand": "Minimalist", "name": "Invisible Sunscreen SPF 40", "benefit": "Gel finish, no white cast", "intensity": 3, "focus": "barrier", "skin_type": "all"},
        {"brand": "Photon", "name": "360 Sunscreen Gel", "benefit": "Broad spectrum (India)", "intensity": 4, "focus": "pigmentation", "skin_type": "all"},
        {"brand": "Fixderma Shadow", "name": "SPF 50+ Gel", "benefit": "Lightweight water-resistant", "intensity": 3, "focus": "barrier", "skin_type": "all"}
    ],
    "moisturizer_gel": [
        {"brand": "Minimalist", "name": "Sepicalm 3% + Oat", "benefit": "Calming lightweight gel-cream", "intensity": 2, "focus": "barrier", "skin_type": "oily"},
        {"brand": "Pond's", "name": "Super Light Gel", "benefit": "High-purity hydration", "intensity": 1, "focus": "barrier", "skin_type": "oily"},
        {"brand": "Dot & Key", "name": "72 HR Hydrating Gel", "benefit": "Cooling cucumber base", "intensity": 1, "focus": "barrier", "skin_type": "all"},
        {"brand": "Neutrogena", "name": "Hydro Boost Water Gel", "benefit": "Clinically proven barrier", "intensity": 2, "focus": "barrier", "skin_type": "oily"}
    ],
    "moisturizer_barrier": [
        {"brand": "Re'equil", "name": "Ceramide & Hyaluronic", "benefit": "Intensive repair (India)", "intensity": 4, "focus": "barrier", "skin_type": "dry"},
        {"brand": "Venusia Max", "name": "Intensive Moisturizing Cream", "benefit": "Strong hydration for dry skin", "intensity": 5, "focus": "barrier", "skin_type": "dry"},
        {"brand": "Minimalist", "name": "Marula Oil Moisturizer", "benefit": "Deeply nourishing (India)", "intensity": 3, "focus": "barrier", "skin_type": "all"},
        {"brand": "CeraVe", "name": "Skin Renewing Night Cream", "benefit": "Peptide-rich overnight healing", "intensity": 4, "focus": "barrier", "skin_type": "all"}
    ]
}

def _derive_skin_profile(analysis: dict) -> dict:
    """Extract granular causes and profile from analysis."""
    severity = analysis.get("acne_severity", {})
    grade = severity.get("grade", "Clear")
    inflamm = severity.get("inflammatory_count", 0)
    comedo = severity.get("comedonal_count", 0)
    pig_cov = analysis.get("hyperpigmentation", {}).get("coverage_pct", 0)
    zones = analysis.get("zone_health", {})
    
    # Derive Primary Cause
    cause = "barrier" # Default
    if inflamm > 3 or grade == "Severe": cause = "inflammation"
    elif comedo > 5: cause = "pores"
    elif pig_cov > 15: cause = "pigmentation"

    # Derive Skin Type
    t_zone_affected = zones.get("forehead", {}).get("status") == "Unhealthy" or \
                      zones.get("nose", {}).get("status") == "Unhealthy"
    u_zone_clear = zones.get("left_cheek", {}).get("status") == "Healthy" and \
                    zones.get("right_cheek", {}).get("status") == "Healthy"
    
    skin_type = "oily" if t_zone_affected else "all"
    if not t_zone_affected and u_zone_clear: skin_type = "dry"

    # Derive Intensity Needs (1-5)
    intensity = 1
    if grade == "Severe": intensity = 5
    elif grade == "Moderate": intensity = 3
    elif grade == "Mild": intensity = 2
    
    return {
        "cause": cause,
        "skin_type": skin_type,
        "intensity": intensity,
        "grade": grade
    }

def _get_products(action_keyword: str, analysis: dict = None) -> list:
    """
    Hyper-Dynamic Product Recommendation logic.
    Scores each product in the library against the user's specific skin profile.
    """
    k = action_keyword.lower()
    profile = _derive_skin_profile(analysis) if analysis else {"cause": "barrier", "skin_type": "all", "intensity": 2}

    # 1. Identify valid category
    category_key = "cleanser_gentle"
    if "benzoyl peroxide" in k: category_key = "cleanser_bp"
    elif "salicylic" in k: category_key = "cleanser_sa"
    elif "gentle" in k or "hydrating" in k: category_key = "cleanser_gentle"
    elif "niacinamide" in k: category_key = "serum_niacinamide"
    elif "vitamin c" in k: category_key = "ser_vitamin_c"
    elif "retinoid" in k or "retinol" in k or "adapalene" in k or "azelaic" in k: category_key = "treatment_retinoid"
    elif "spf" in k or "shield" in k: category_key = "spf"
    elif "gel" in k or "oil-free" in k: category_key = "moisturizer_gel"
    elif "barrier" in k or "balm" in k or "heavy" in k or "intensive" in k: category_key = "moisturizer_barrier"
    elif "cleanser" in k: category_key = "cleanser_gentle"
    elif "moisturizer" in k: category_key = "moisturizer_barrier"

    products = PRODUCT_LIBRARY.get(category_key, PRODUCT_LIBRARY["cleanser_gentle"])

    # 2. Score products based on Causes and Skin Profile
    scored_products = []
    for p in products:
        score = 0
        
        # Match Focus (The "Cause") - Weight: 5
        if p.get("focus") == profile["cause"]:
            score += 5
        
        # Match Skin Type - Weight: 3 (Penalty for mismatch)
        if p.get("skin_type") == profile["skin_type"]:
            score += 3
        elif p.get("skin_type") != "all":
            score -= 3 # Strong penalty for incompatible skin type
            
        # Match Intensity - Weight: 2
        intensity_diff = abs(p.get("intensity", 1) - profile["intensity"])
        score += (5 - intensity_diff) # Better match = higher score
        
        scored_products.append({"prod": p, "score": score})

    # 3. Sort by score and return top results
    scored_products.sort(key=lambda x: x["score"], reverse=True)
    return [x["prod"] for x in scored_products[:4]]

def generate_recommendations(analysis: dict) -> dict:
    """
    Generate personalized skincare recommendations.
    Uses hyper-dynamic weighted logic to pick the best products for the detected cause.
    """
    severity = analysis.get("acne_severity", {})
    grade = severity.get("grade", "Clear")
    lesion_count = analysis.get("lesion_count", 0)
    inflammatory = severity.get("inflammatory_count", 0)
    comedonal = severity.get("comedonal_count", 0)
    pigmentation = analysis.get("hyperpigmentation", {})
    pig_coverage = pigmentation.get("coverage_pct", 0)
    zones = analysis.get("zone_health", {})

    dark_spots = severity.get("dark_spot_count", 0)

    # Initial Routines
    am_routine = _get_am_routine(grade, inflammatory, comedonal, pig_coverage, zones)
    pm_routine = _get_pm_routine(grade, inflammatory, comedonal, pig_coverage, zones)

    # Attach Products contextually
    for step in am_routine:
        step["recommended_products"] = _get_products(step["action"], analysis)
    for step in pm_routine:
        step["recommended_products"] = _get_products(step["action"], analysis)

    recommendations = {
        "summary": _get_summary(grade, lesion_count, dark_spots, pig_coverage),
        "am_routine": am_routine,
        "pm_routine": pm_routine,
        "key_ingredients": _get_key_ingredients(grade, inflammatory, dark_spots, pig_coverage),
        "lifestyle": _get_lifestyle_tips(grade, zones),
        "warnings": _get_warnings(grade, inflammatory),
        "confidence_note": "This is an AI-generated, non-diagnostic screening. Always consult a dermatologist for medical advice.",
    }

    return recommendations


def _get_summary(grade: str, lesion_count: int, dark_spots: int, pig_coverage: float) -> str:
    """Generate analysis summary."""
    spot_text = f" and {dark_spots} dark spot(s)" if dark_spots > 0 else ""
    summaries = {
        "Clear": f"Your skin appears healthy with no significant lesions detected. "
                 f"Hyperpigmentation coverage is at {pig_coverage}%. Focus on protection and barrier maintenance.",
        "Mild": f"Mild acne detected with {lesion_count} lesion(s){spot_text}. "
                f"A targeted routine focusing on gentle exfoliation will clear this within 4 weeks.",
        "Moderate": f"Moderate acne detected with {lesion_count} lesion(s){spot_text}. "
                    f"Prioritizing anti-inflammatory actives and pore regulation is recommended.",
        "Severe": f"Significant acne detected with {lesion_count} lesion(s){spot_text}. "
                  f"Professional consultation is recommended to prevent scarring while starting this soothing routine.",
    }
    return summaries.get(grade, summaries["Clear"])


def _get_am_routine(grade: str, inflammatory: int, comedonal: int, pig_coverage: float, zones: dict) -> list:
    """Generate highly dynamic morning routine steps."""
    routine = []
    
    # Step 1: DYNAMIC CLEANSER
    if inflammatory > 5 or grade == "Severe":
        cleanser = {
            "step": 1,
            "action": "Benzoyl Peroxide 4% Wash",
            "detail": "Use a creamy BP wash (4%) to kill acne bacteria without over-drying. Leave on for 1 min before rinsing.",
            "ingredients": ["Benzoyl Peroxide 4%", "Glycerin", "Ceramides"],
        }
    elif comedonal > 3 or grade == "Moderate":
        cleanser = {
            "step": 1,
            "action": "Salicylic Acid 2% Cleanser",
            "detail": "Gently exfoliates inside pores to clear blackheads and prevent new breakouts.",
            "ingredients": ["Salicylic Acid 2%", "Zinc PCA", "Aloe Vera"],
        }
    elif pig_coverage > 10:
        cleanser = {
            "step": 1,
            "action": "Brightening AHA Cleanser",
            "detail": "Lather gently to remove dead skin cells and improve overall radiance.",
            "ingredients": ["Glycolic Acid", "Lactic Acid", "Licorice Root"],
        }
    else:
        cleanser = {
            "step": 1,
            "action": "Gentle Hydrating Cleanser",
            "detail": "Maintain your healthy skin barrier with a pH-balanced, non-stripping formula.",
            "ingredients": ["Ceramides", "Hyaluronic Acid", "Squalane"],
        }
    routine.append(cleanser)

    # Step 2: TARGETED AM SERUM
    if inflammatory > 2:
        routine.append({
            "step": 2,
            "action": "Azelaic Acid 10% Suspension",
            "detail": "Apply to red, inflamed areas. It significantly reduces redness and prevents post-acne marks.",
            "ingredients": ["Azelaic Acid", "Centella Asiatica"],
        })
    elif pig_coverage > 10 or grade == "Mild":
        routine.append({
            "step": 2,
            "action": "Vitamin C + Ferulic Acid",
            "detail": "Powerful antioxidant protection to brighten skin and neutralize environmental damage.",
            "ingredients": ["L-Ascorbic Acid 15%", "Ferulic Acid", "Vitamin E"],
        })
    
    # Step 3: MOISTURIZER (By Zone/Type)
    is_oily = zones.get("forehead", {}).get("affected") or zones.get("nose", {}).get("affected")
    if grade == "Severe" or (inflammatory > 5):
        moisturizer = {
            "step": len(routine) + 1,
            "action": "Barrier Repair Cream",
            "detail": "Rich, soothing balm to protect skin while it's in an active inflammatory state.",
            "ingredients": ["Ceramide NP", "Peptides", "Panthenol"],
        }
    elif is_oily:
        moisturizer = {
            "step": len(routine) + 1,
            "action": "Oil-Free Water Gel",
            "detail": "Ultra-lightweight hydration that won't clog pores in oily regions.",
            "ingredients": ["Hyaluronic Acid", "Rosewater", "Glycerin"],
        }
    else:
        moisturizer = {
            "step": len(routine) + 1,
            "action": "Daily Light Moisturizer",
            "detail": "Balanced hydration suitable for your current skin profile.",
            "ingredients": ["Squalane", "Niacinamide", "Vitamin B5"],
        }
    routine.append(moisturizer)

    # Step 4: PROTECTION (Always Required)
    routine.append({
        "step": len(routine) + 1,
        "action": "Mineral SPF 50+ Invisible Shield",
        "detail": "Essential. UV rays darken hyperpigmentation and cause acne inflammation to linger longer.",
        "ingredients": ["Zinc Oxide", "Titanium Dioxide", "Artemisia Extract"],
    })

    return routine


def _get_pm_routine(grade: str, inflammatory: int, comedonal: int, pig_coverage: float, zones: dict) -> list:
    """Generate highly dynamic evening routine steps."""
    routine = []
    
    # Step 1: DOUBLE CLEANSE (Base logic)
    if pig_coverage > 15 or grade in ["Moderate", "Severe"]:
        routine.append({
            "step": 1,
            "action": "Deep Oil Cleanser + Gel Wash",
            "detail": "The 'Double Cleanse' method ensures all SPF and deep-seated sebum are removed.",
            "ingredients": ["Jojoba Oil", "Sea Buckthorn", "Green Tea Wash"],
        })
    else:
        routine.append({
            "step": 1,
            "action": "Gentle Gel Cleanser",
            "detail": "Remove daily impurities without compromising the skin's natural oils.",
            "ingredients": ["Oat Protein", "Glycerin"],
        })

    # Step 2: PRIMARY TREATMENT BRANCH
    if grade == "Clear":
        routine.append({
            "step": 2,
            "action": "Niacinamide 10% Barrier Serum",
            "detail": "Regulates oil production and keeps pores refined for long-term clarity.",
            "ingredients": ["Niacinamide", "Zinc PCA"],
        })
    elif grade == "Mild" or comedonal > 5:
        routine.append({
            "step": 2,
            "action": "Adapalene (Retinoid) 0.1%",
            "detail": "The gold standard for comedonal acne. Speeds up cell turnover to purge clogged pores.",
            "ingredients": ["Adapalene", "Methylparaben (safe preservative)"],
        })
    elif grade == "Moderate" or inflammatory > 3:
        routine.append({
            "step": 2,
            "action": "Micro-Encapsulated Retinol",
            "detail": "Time-released retinoid that treats acne and texture with reduced irritation risk.",
            "ingredients": ["Retinol 0.3%", "Peptides", "Allantoin"],
        })
    else: # Severe
        routine.append({
            "step": 2,
            "action": "Soothing Cica Ampoule",
            "detail": "Focus on calming the intense inflammation before introducing heavy actives.",
            "ingredients": ["Centella Asiatica 95%", "Madecassoside"],
        })

    # Step 3: BRIGHTENING BOOST (If needed)
    if pig_coverage > 20:
        routine.append({
            "step": len(routine) + 1,
            "action": "Tranexamic Acid Serum",
            "detail": "Targets the pathway that leads to dark spot formation (melasma/PIH).",
            "ingredients": ["Tranexamic Acid 3%", "Alpha Arbutin", "Kojic Acid"],
        })

    # Step 4: NIGHT MOISTURIZER
    if grade == "Severe" or inflammatory > 10:
        moisturizer = {
            "step": len(routine) + 1,
            "action": "Intensive Recovery Balm",
            "detail": "A thicker seal to prevent 'Transepidermal Water Loss' overnight.",
            "ingredients": ["Shea Butter", "Colloidal Oatmeal", "Ceramides"],
        }
    else:
        moisturizer = {
            "step": len(routine) + 1,
            "action": "Multi-Peptide Night Cream",
            "detail": "Hydrates and supports skin repair processes while you sleep.",
            "ingredients": ["Matrixyl 3000", "Hyaluronic Acid", "Copper Peptides"],
        }
    routine.append(moisturizer)

    return routine


def _get_key_ingredients(grade: str, inflammatory: int, dark_spots: int, pig_coverage: float) -> list:
    """Get prioritized key ingredients with dynamic priority levels."""
    ingredients = []

    if inflammatory > 5:
        ingredients.append({"name": "Benzoyl Peroxide", "purpose": "Kills acne bacteria", "priority": "CRITICAL"})
    
    if inflammatory > 2:
        ingredients.append({"name": "Azelaic Acid", "purpose": "Reduces redness & PIE", "priority": "high"})
        ingredients.append({"name": "Centella Asiatica (Cica)", "purpose": "Intense skin soothing", "priority": "high"})

    if grade in ["Moderate", "Severe"] or dark_spots > 2:
        ingredients.append({"name": "Retinoids (Adapalene/Retinol)", "purpose": "Cell turnover & anti-acne", "priority": "high"})

    if pig_coverage > 10 or dark_spots > 1:
        ingredients.append({"name": "Vitamin C", "purpose": "Brightening & UV repair", "priority": "high"})
        ingredients.append({"name": "Alpha Arbutin", "purpose": "Fades dark spots", "priority": "medium"})
        ingredients.append({"name": "Tranexamic Acid", "purpose": "Targets deep pigmentation", "priority": "medium"})

    # Always add baseline health ingredients
    ingredients.append({"name": "Ceramides", "purpose": "Barrier protection", "priority": "high"})
    ingredients.append({"name": "SPF 50+", "purpose": "Prevention of all conditions", "priority": "CRITICAL"})

    return ingredients[:6] # Limit to top 6


def _get_lifestyle_tips(grade: str, zones: dict) -> list:
    """Generate lifestyle recommendations based on patterns."""
    tips = [
        "Drink at least 8 glasses of water daily for skin hydration",
        "Change pillowcases every 2 days to reduce bacteria build-up",
    ]

    # Pattern: Chin breakouts -> Minimal hormonal tip
    if zones.get("chin_jawline", {}).get("affected"):
        tips.append("Lower face breakouts can be hormonal; prioritize sleep and stress management.")

    # Pattern: Oily zones -> Double cleanse tip
    if zones.get("forehead", {}).get("affected") or zones.get("nose", {}).get("affected"):
        tips.append("Focus your double-cleansing more on the T-zone (forehead and nose).")

    if grade in ["Moderate", "Severe"]:
        tips.append("Try a low-glycemic diet; high sugar can trigger insulin spikes and acne.")
        tips.append("Clean your phone screen daily to avoid transferring bacteria to cheeks.")

    return tips


def _get_warnings(grade: str, inflammatory: int) -> list:
    """Generate important warnings."""
    warnings = []

    if grade == "Severe":
        warnings.append(
            "⚠️ Severe acne detected — professional dermatological evaluation is strongly recommended to prevent permanent scarring."
        )

    if inflammatory > 8:
        warnings.append(
            "⚠️ High inflammation — do NOT pick or squeeze lesions. This can lead to deep infection and cystic nodules."
        )

    warnings.append(
        "ℹ️ This is an AI-powered screening tool and does NOT constitute medical diagnosis. Always consult a professional."
    )

    return warnings
