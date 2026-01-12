
# Health Plan Definitions and Rules

PLANS = [
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

def recommend_plan(conditions):
    """
    Recommend a plan based on the patient's active conditions.
    Logic: Find the cheapest plan that covers ALL the patient's conditions.
    """
    if not conditions:
        return PLANS[0] # Return Basic if no conditions

    condition_names = [c.get("code", {}).get("text", "") for c in conditions]
    
    # Simple logic: If any condition is "Severe" or not covered by lower tiers, bump up.
    # We will iterate through plans from cheapest to most expensive.
    
    for plan in PLANS:
        if "ALL" in plan["coverage"]:
            return plan
        
        covered_count = 0
        for cond_name in condition_names:
            # Check if this condition is covered by the plan
            # (Matches if the condition string contains one of the coverage keywords)
            if any(c.lower() in cond_name.lower() for c in plan["coverage"]):
                covered_count += 1
        
        # If this plan covers all specific conditions gathered, recommend it
        if covered_count == len(condition_names):
            return plan

    # Default to Comprehensive if nothing else fits (or mixed complex conditions)
    return PLANS[-1]
