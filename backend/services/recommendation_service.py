
# Health Plan Definitions and Rules

from models.insurance_plan_model import InsurancePlanModel

# Default plans for fallback/seeding
DEFAULT_PLANS = [
    {
        "id": "basic",
        "name": "Basic Care",
        "cost": 50,
        "description": "Covers basic seasonal illnesses like cold, fever, and minor infections.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache"]
    },
    {
        "id": "standard",
        "name": "Standard Care",
        "cost": 100,
        "description": "Includes Basic coverage plus common chronic conditions management (early stage).",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis"]
    },
    {
        "id": "gold",
        "name": "Gold Premium",
        "cost": 200,
        "description": "Comprehensive coverage including diabetes management and moderate conditions.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis", "Diabetes mellitus", "Asthma"]
    },
    {
        "id": "platinum",
        "name": "Platinum Elite",
        "cost": 350,
        "description": "Full coverage for serious chronic conditions, cardiac issues, and surgeries.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis", "Diabetes mellitus", "Asthma", "Coronary heart disease", "Fracture"]
    },
    {
        "id": "comprehensive",
        "name": "Universal Comprehensive",
        "cost": 500,
        "description": "Total coverage for all known conditions, rare diseases, and long-term care.",
        "coverage": ["ALL"]  # Special flag
    }
]

def get_all_plans():
    """Fetch plans from DB or use defaults if empty."""
    model = InsurancePlanModel()
    plans = model.find_all()
    if not plans:
        # Auto-seed if empty
        print("Auto-seeding plans...")
        for p in DEFAULT_PLANS:
            model.create(p)
        plans = model.find_all()
    
    # Format for usage (remove _id if needed or handle it)
    results = []
    if plans:
        for p in plans:
            p['id'] = str(p['_id'])
            del p['_id']
            results.append(p)
            
    return results or DEFAULT_PLANS

def recommend_plan(conditions):
    """
    Recommend a plan based on the patient's active conditions.
    Logic: Find the cheapest plan that covers ALL the patient's conditions.
    """
    plans = get_all_plans()
    
    # Sort plans by cost to ensure we find cheapest first
    # Assuming 'cost' is present.
    try:
        plans.sort(key=lambda x: x.get("cost", 9999))
    except:
        pass

    if not conditions:
        return plans[0] # Return Basic (cheapest) if no conditions

    condition_names = [c.get("code", {}).get("text", "") for c in conditions]
    
    for plan in plans:
        coverage = plan.get("coverage", [])
        if "ALL" in coverage:
            return plan
        
        covered_count = 0
        for cond_name in condition_names:
            if any(c.lower() in cond_name.lower() for c in coverage):
                covered_count += 1
        
        if covered_count == len(condition_names):
            return plan

    # Default to most expensive if nothing else fits
    return plans[-1]

from datetime import datetime
from models.models import PatientModel, ConditionModel
from models.risk_assessment_model import RiskAssessmentModel

def find_similar_patients(target_patient_id):
    """
    Finds a cohort of similar patients based on:
    - Gender (Exact match)
    - Age Group (+/- 5 years)
    - Risk Label (Same category)
    - Shared Conditions
    """
    patient_model = PatientModel()
    condition_model = ConditionModel()
    risk_model = RiskAssessmentModel()
    
    # 1. Get Target Patient Data
    target_patient = patient_model.find_by_id(target_patient_id)
    if not target_patient: return []
    
    target_gender = target_patient.get("gender")
    target_dob_str = target_patient.get("birthDate")
    target_conditions = condition_model.find_by_patient(target_patient_id)
    target_condition_codes = {c.get("code", {}).get("text") for c in target_conditions}
    
    target_risk = risk_model.find_latest_by_patient(target_patient_id)
    target_risk_label = "Unknown"
    if target_risk:
        target_risk_label = target_risk.get("prediction", [{}])[0].get("qualitativeRisk", {}).get("coding", [{}])[0].get("display")

    # Calculate Target Age
    target_age = 0
    if target_dob_str:
        try:
            dob = datetime.strptime(target_dob_str, "%Y-%m-%d")
            target_age = (datetime.now() - dob).days // 365
        except: pass
        
    # 2. Find Candidates (Filter by Gender first for speed)
    # Note: In a real large DB, we'd use a more specific query. Here we scan filtered list.
    candidates = patient_model.collection.find({"gender": target_gender})
    
    scored_candidates = []
    
    for cand in candidates:
        cand_id = str(cand["_id"])
        if cand_id == target_patient_id: continue # Skip self
        
        score = 0
        reasons = []
        
        # Gender Match (Already filtered, but +1 for base similarity)
        score += 1 
        
        # Age Match
        cand_dob_str = cand.get("birthDate")
        if cand_dob_str:
            try:
                c_dob = datetime.strptime(cand_dob_str, "%Y-%m-%d")
                c_age = (datetime.now() - c_dob).days // 365
                if abs(c_age - target_age) <= 5:
                    score += 2
                    reasons.append(f"Similar Age ({c_age})")
            except: pass
            
        # Risk Match
        cand_risk = risk_model.find_latest_by_patient(cand_id)
        if cand_risk:
            c_label = cand_risk.get("prediction", [{}])[0].get("qualitativeRisk", {}).get("coding", [{}])[0].get("display")
            if c_label == target_risk_label:
                score += 3
                reasons.append(f"Same Risk Level ({c_label})")
        
        # Condition Overlap
        cand_conditions = condition_model.find_by_patient(cand_id)
        cand_codes = {c.get("code", {}).get("text") for c in cand_conditions}
        shared = target_condition_codes.intersection(cand_codes)
        if shared:
            score += len(shared)
            reasons.append(f"Shared Conditions: {', '.join(shared)}")
            
        if score > 0:
            scored_candidates.append({
                "patient_id": cand_id,
                "name": cand.get("name", [{}])[0].get("text", "Unknown"),
                "similarity_score": score,
                "reasons": reasons
            })
            
    # Sort by score desc
    return sorted(scored_candidates, key=lambda x: x["similarity_score"], reverse=True)[:5]


def get_insurance_recommendation_for_patient(patient_id):
    """
    7) Insurance Recommendation
    - Identify similar patients
    - Recommend plan using Logic:
      - LOW Risk -> Basic
      - MEDIUM Risk -> Standard / Gold
      - HIGH Risk -> Gold / Platinum
    - Also consider what similar patients have (simulated preference)
    """
    # 1. Get Risk Level
    risk_model = RiskAssessmentModel()
    risk = risk_model.find_latest_by_patient(patient_id)
    
    # Default to Low if no risk found
    risk_label = "Low"
    if risk:
        risk_label = risk.get("prediction", [{}])[0].get("qualitativeRisk", {}).get("coding", [{}])[0].get("display")

    # 2. Base Recommendation by Risk
    recommended_plan_ids = []
    reason_text = f"Based on your {risk_label} risk profile."
    
    if risk_label == "Low":
        recommended_plan_ids = ["basic"]
    elif risk_label == "Medium":
        recommended_plan_ids = ["standard", "gold"]
    else: # High
        recommended_plan_ids = ["gold", "platinum"]
        
    # 3. Augment with Similar Patient Preferences
    # (Since we don't have an enrolledPlan field in Patient yet, we will just simulate this logic 
    # by saying "People like you also frequently choose... X")
    
    # Get similar patients
    similar = find_similar_patients(patient_id)
    sim_text = ""
    if similar:
        sim_text = f" {len(similar)} similar patients were analyzed to refine this suggestion."
        
    plans = get_all_plans()
    recommendations = []
    
    for plan in plans:
        if plan["id"] in recommended_plan_ids:
            recommendations.append(plan)
            
    return {
        "risk_level": risk_label,
        "recommended_plans": recommendations,
        "explanation": reason_text + sim_text
    }

