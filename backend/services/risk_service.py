from datetime import datetime
from models.risk_assessment_model import RiskAssessmentModel
from models.models import ObservationModel, MedicationModel

risk_model = RiskAssessmentModel()
observation_model = ObservationModel()
medication_model = MedicationModel()

def calculate_risk_score(patient, conditions):
    """
    Calculates a rule-based risk score:
    - Age score (max 30)
    - Condition score (max 40)
    - Observation score (max 20)
    - Medication score (max 10)
    
    Total score mapped to:
    - 0–30 → LOW
    - 31–60 → MEDIUM
    - 61–100 → HIGH
    """
    score = 0
    details = []
    
    # 1. Age Score (Max 30)
    birth_date = patient.get("birthDate")
    age = 0
    if birth_date:
        try:
            dob = datetime.strptime(birth_date, "%Y-%m-%d")
            age = (datetime.now() - dob).days // 365
            
            age_score = 0
            if age > 60: age_score = 30
            elif age > 45: age_score = 20
            elif age > 30: age_score = 10
            else: age_score = 5
            
            score += age_score
            details.append(f"Age {age}: +{age_score}")
        except:
            pass # Invalid date

    # 2. Condition Score (Max 40)
    # High risk keywords
    high_risk = ["diabetes", "hypertension", "heart", "cancer", "stroke", "asthma"]
    cond_score = 0
    for condition in conditions:
        text = condition.get("code", {}).get("text", "").lower()
        if any(hr in text for hr in high_risk):
            cond_score += 15
        else:
            cond_score += 5
            
    # Cap at 40
    if cond_score > 40: cond_score = 40
    score += cond_score
    details.append(f"Conditions: +{cond_score}")

    # 3. Observation Score (Max 20)
    # Check for recent bad vitals
    patient_id = str(patient.get("_id")) if "_id" in patient else patient.get("id")
    observations = observation_model.find_by_patient(patient_id)
    obs_score = 0
    
    for obs in observations:
        text = obs.get("code", {}).get("text", "").lower()
        val = obs.get("valueQuantity", {}).get("value", 0)
        
        # BP > 140
        if ("blood pressure" in text or "systolic" in text) and val > 140:
            obs_score += 10
        # Sugar > 180
        elif ("glucose" in text or "sugar" in text) and val > 180:
            obs_score += 10
            
    if obs_score > 20: obs_score = 20
    score += obs_score
    details.append(f"Vitals: +{obs_score}")

    # 4. Medication Score (Max 10)
    # More meds = higher complexity/risk
    meds = medication_model.find_by_patient(patient_id)
    med_score = min(len(meds) * 5, 10)
    score += med_score
    details.append(f"Meds ({len(meds)}): +{med_score}")
    
    # Clip Total Score to 100
    if score > 100: score = 100

    # Determine Label
    if score <= 30:
        label = "Low"
    elif score <= 60:
        label = "Medium"
    else:
        label = "High"
    
    # Save RiskAssessment
    risk_assessment = {
        "resourceType": "RiskAssessment",
        "status": "final",
        "subject": {"reference": f"Patient/{patient_id}"},
        "occurrenceDateTime": datetime.now().isoformat(),
        "prediction": [{
            "outcome": {"text": "General Health Risk"},
            "qualitativeRisk": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/risk-probability",
                    "code": label.lower(),
                    "display": label
                }]
            },
            "probabilityDecimal": score
        }],
        "note": [{"text": " | ".join(details)}]
    }
    
    inserted_id = risk_model.create(risk_assessment)
    risk_assessment["id"] = str(inserted_id)
    if "_id" in risk_assessment: del risk_assessment["_id"]
    
    return risk_assessment
