from datetime import datetime
from models.risk_assessment_model import RiskAssessmentModel
from models.models import ObservationModel, MedicationModel

risk_model = RiskAssessmentModel()
observation_model = ObservationModel()
medication_model = MedicationModel()

def calculate_risk_score(patient, conditions, weights=None):
    """
    Calculates a rule-based risk score with customizable weights.
    Default Weights:
    - Age score: 30
    - Condition score: 40
    - Observation score: 20
    - Medication score: 10
    """
    if not weights:
        weights = {
            "age": 30,
            "conditions": 40,
            "observations": 20,
            "medications": 10
        }
    
    score = 0
    details = []
    
    # 1. Age Score
    birth_date = patient.get("birthDate")
    age_component = 0
    if birth_date:
        try:
            if isinstance(birth_date, str):
                dob = datetime.strptime(birth_date, "%Y-%m-%d")
            else:
                dob = birth_date
            
            age = (datetime.now() - dob).days // 365
            
            factor = 0
            if age > 60: factor = 1.0
            elif age > 45: factor = 0.66
            elif age > 30: factor = 0.33
            else: factor = 0.16
            
            age_component = factor * weights.get("age", 30)
            score += age_component
            details.append(f"Age {age}: +{round(age_component, 1)}")
        except:
            pass 

    # 2. Condition Score
    high_risk = ["diabetes", "hypertension", "heart", "cancer", "stroke", "asthma"]
    cond_raw_score = 0
    for condition in conditions:
        text = condition.get("code", {}).get("text", "").lower()
        if any(hr in text for hr in high_risk):
            cond_raw_score += 1.0
        else:
            cond_raw_score += 0.3
            
    cond_component = min(cond_raw_score * 15, weights.get("conditions", 40))
    score += cond_component
    details.append(f"Conditions: +{round(cond_component, 1)}")

    # 3. Observation Score
    patient_id = str(patient.get("_id")) if "_id" in patient else patient.get("id")
    observations = observation_model.find_by_patient(patient_id)
    obs_raw_score = 0
    
    for obs in observations:
        text = obs.get("code", {}).get("text", "").lower()
        val_obj = obs.get("valueQuantity", {})
        val = val_obj.get("value", 0) if isinstance(val_obj, dict) else 0
        
        if ("blood pressure" in text or "systolic" in text) and val > 140:
            obs_raw_score += 0.5
        elif ("glucose" in text or "sugar" in text) and val > 180:
            obs_raw_score += 0.5
            
    obs_component = min(obs_raw_score * 20, weights.get("observations", 20))
    score += obs_component
    details.append(f"Vitals: +{round(obs_component, 1)}")

    # 4. Medication Score
    meds = medication_model.find_by_patient(patient_id)
    med_raw_score = len(meds) * 0.5
    med_component = min(med_raw_score * 10, weights.get("medications", 10))
    score += med_component
    details.append(f"Meds ({len(meds)}): +{round(med_component, 1)}")
    
    if score > 100: score = 100

    if score <= 30:
        label = "Low"
    elif score <= 60:
        label = "Medium"
    else:
        label = "High"
    
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
            "probabilityDecimal": round(score, 1)
        }],
        "note": [{"text": " | ".join(details)}]
    }
    
    # Save RiskAssessment ONLY if default weights are used
    is_default = weights == {"age": 30, "conditions": 40, "observations": 20, "medications": 10}
    if is_default:
        inserted_id = risk_model.create(risk_assessment)
        risk_assessment["id"] = str(inserted_id)
        if "_id" in risk_assessment: del risk_assessment["_id"]
    
    return risk_assessment
