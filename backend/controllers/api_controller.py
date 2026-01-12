from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
from models.models import PatientModel, ConditionModel, ObservationModel, MedicationModel, UserModel, HistoryModel, ClinicalVersionModel
from services.recommendation_service import get_all_plans, recommend_plan
from services.risk_service import calculate_risk_score
from utils.validation import validate_fhir_resource
from data.scripts import conditions_pool, observations_pool, medications_pool

api = Blueprint('api', __name__)
# ... (existing model initializations)

@api.route('/registration-data', methods=['GET'])
def get_registration_data():
    return jsonify({
        "conditions": conditions_pool,
        "observations": observations_pool,
        "medications": medications_pool
    })

patient_model = PatientModel()
condition_model = ConditionModel()
observation_model = ObservationModel()
medication_model = MedicationModel()
user_model = UserModel()
history_model = HistoryModel()
version_model = ClinicalVersionModel()

def format_id(doc):
    if doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# --- Auth ---
@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = user_model.find_by_username(username)
    if user and user.get("password") == password:
        token = create_access_token(identity=username, additional_claims={"role": user.get("role")})
        return jsonify({
            "token": token,
            "role": user.get("role"), 
            "name": user.get("name"), 
            "id": str(user.get("_id")),
            "patientId": user.get("patientId")
        })
        
    return jsonify({"error": "Invalid credentials"}), 401

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    
    if user_model.find_by_username(username):
         return jsonify({"error": "Username already exists"}), 400

    # Validate Patient Data (Manually constructing FHIR Patient for minimal check)
    patient_details = data.get('patientDetails')
    patient_data = {
        "resourceType": "Patient",
        "name": [{"text": f"{patient_details.get('firstName')} {patient_details.get('lastName')}"}],
        "gender": patient_details.get("gender"),
        "birthDate": patient_details.get("birthDate"),
        "telecom": [{"system": "phone", "value": patient_details.get("mobile")}],
        "address": [{"text": patient_details.get("address")}]
    }
    
    # Strict Validation
    validated_patient, error = validate_fhir_resource("Patient", patient_data)
    if error:
        return jsonify({"error": f"Invalid FHIR Patient Data: {error}"}), 400

    patient_id = patient_model.create(validated_patient)
    patient_id_str = str(patient_id)
    
    from utils.validation import sanitize_text

    # 1. Conditions (Multi-select)
    conditions = data.get('conditions', [])
    for c_text in conditions:
        clean_text = sanitize_text(c_text)
        if clean_text and clean_text in conditions_pool:
            c_data = {
                "resourceType": "Condition",
                "clinicalStatus": {"text": "Active"},
                "code": {"text": clean_text},
                "subject": {"reference": f"Patient/{patient_id_str}"}
            }
            val_c, err = validate_fhir_resource("Condition", c_data)
            if not err: condition_model.create(val_c)

    # 1.5 Medications (Multi-select)
    medications = data.get('medications', [])
    for m_text in medications:
        clean_text = sanitize_text(m_text)
        if clean_text and clean_text in medications_pool:
            # Note: fhir.resources (R5) expects 'medication' with 'concept'
            m_data = {
                "resourceType": "MedicationRequest",
                "status": "active",
                "intent": "order",
                "medication": {"concept": {"text": clean_text}},
                "subject": {"reference": f"Patient/{patient_id_str}"}
            }
            val_m, err = validate_fhir_resource("MedicationRequest", m_data)
            if not err: 
                medication_model.create(val_m)

    # 2. Vitals (Observations)
    vitals = data.get('vitals', {})
    VITAL_MAP = {
        "systolic": {"code": "8480-6", "display": "Systolic blood pressure", "unit": "mmHg"},
        "diastolic": {"code": "8462-4", "display": "Diastolic blood pressure", "unit": "mmHg"},
        "heartRate": {"code": "8867-4", "display": "Heart rate", "unit": "beats/min"},
        "weight": {"code": "29463-7", "display": "Body Weight", "unit": "kg"},
        "height": {"code": "8302-2", "display": "Body Height", "unit": "cm"}
    }
    
    for key, value in vitals.items():
        if value and str(value).strip():
            try:
                 val_num = float(value)
            except:
                 continue 
                 
            meta = VITAL_MAP.get(key)
            if meta:
                o_data = {
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": meta["code"],
                            "display": meta["display"]
                        }],
                        "text": meta["display"]
                    },
                    "subject": {"reference": f"Patient/{patient_id_str}"},
                    "valueQuantity": {
                        "value": val_num,
                        "unit": meta["unit"],
                        "system": "http://unitsofmeasure.org",
                        "code": meta["unit"]
                    },
                    "effectiveDateTime": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                val_o, err = validate_fhir_resource("Observation", o_data)
                if not err: observation_model.create(val_o)

    # 2.5 Extra Observations
    extras = vitals.get('extras', [])
    for obs in extras:
        obs_name = sanitize_text(obs.get('name'))
        obs_value = obs.get('value')
        obs_unit = obs.get('unit')
        
        if obs_name and obs_value:
            try:
                val_num = float(obs_value)
            except:
                continue
                
            # Basic validation against pool (optional but good)
            o_data = {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": obs_name},
                "subject": {"reference": f"Patient/{patient_id_str}"},
                "valueQuantity": {
                    "value": val_num,
                    "unit": obs_unit,
                    "system": "http://unitsofmeasure.org",
                    "code": obs_unit
                },
                "effectiveDateTime": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            val_o, err = validate_fhir_resource("Observation", o_data)
            if not err: observation_model.create(val_o)


    # 3. Create initial clinical version (v1)
    version_model.create(patient_id_str, conditions, vitals, 1, medications=medications)

    # 4. Insurance (Coverage)
    insurance_provider = sanitize_text(data.get('insuranceProvider'))
    if insurance_provider:
        # Manual FHIR R4 Construction to avoid R5 Library Mismatch
        # R4 Requirement: 'payor' (List), 'class' (List), no 'kind'
        cov_data = {
            "resourceType": "Coverage",
            "status": "active",
            "beneficiary": {"reference": f"Patient/{patient_id_str}"},
            "payor": [{"display": insurance_provider}],
            "class": [{
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/coverage-class", 
                        "code": "plan"
                    }]
                },
                "name": "Standard Plan",
                "value": "std"
            }]
        }
        # Direct save to MongoDB (Bypassing fhir.resources which enforces R5)
        coverage_model.create(cov_data)

    # Create User
    user_data = {
        "username": sanitize_text(username),
        "password": data.get('password'),
        "role": "patient",
        "name": f"{patient_details.get('firstName')} {patient_details.get('lastName')}",
        "patientId": patient_id_str
    }
    user_model.create(user_data)
    
    return jsonify({"message": "Registration successful", "patientId": patient_id_str}), 201

# --- Generic CRUD Helper ---
def handle_crud(model, resource_type):
    if request.method == 'GET':
        item_id = request.args.get('id')
        patient_id = request.args.get('patient')
        
        if item_id:
            item = model.find_by_id(item_id)
            if item:
                return jsonify(format_id(item))
            return jsonify({"error": f"{resource_type} not found"}), 404
            
        if patient_id:
            items = model.find_by_patient(patient_id)
        else:
            items = model.find_all()
        return jsonify([format_id(i) for i in items])
        
    elif request.method == 'POST':
        data = request.json
        validated_data, error = validate_fhir_resource(resource_type, data)
        if error:
            return jsonify({"error": error}), 400
        inserted_id = model.create(validated_data)
        return jsonify({"id": str(inserted_id)}), 201
        
    elif request.method == 'PUT':
        item_id = request.args.get('id')
        if not item_id:
            return jsonify({"error": "ID is required for update"}), 400
            
        data = request.json
        
        # Archive current version before update for Condition and Medication
        if resource_type in ["Condition", "MedicationRequest"]:
            current_item = model.find_by_id(item_id)
            if current_item:
                history_model.create(item_id, resource_type, current_item)
        
        if model.update(item_id, data):
            return jsonify({"message": f"{resource_type} updated successfully"}), 200
        return jsonify({"error": f"{resource_type} not found or update failed"}), 404

# --- Resources ---

@api.route('/Patient', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def patient_resource():
    # If PUT, we might want to check the ID from the URL or body
    # For now, handle_crud handles ?id=...
    return handle_crud(patient_model, "Patient")

@api.route('/Condition', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def condition_resource():
    return handle_crud(condition_model, "Condition")

@api.route('/Observation', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def observation_resource():
    return handle_crud(observation_model, "Observation")

@api.route('/Medication', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def medication_resource():
    return handle_crud(medication_model, "MedicationRequest")

# --- History Endpoints ---

@api.route('/Condition/<id>/history', methods=['GET'])
@jwt_required()
def condition_history(id):
    history = history_model.find_by_original_id(id)
    formatted_history = []
    for entry in history:
        entry['id'] = str(entry['_id'])
        del entry['_id']
        if 'data' in entry and '_id' in entry['data']:
            entry['data']['id'] = str(entry['data']['_id'])
            del entry['data']['_id']
        formatted_history.append(entry)
    return jsonify(formatted_history)

@api.route('/Medication/<id>/history', methods=['GET'])
@jwt_required()
def medication_history(id):
    history = history_model.find_by_original_id(id)
    formatted_history = []
    for entry in history:
        entry['id'] = str(entry['_id'])
        del entry['_id']
        if 'data' in entry and '_id' in entry['data']:
            entry['data']['id'] = str(entry['data']['_id'])
            del entry['data']['_id']
        formatted_history.append(entry)
    return jsonify(formatted_history)

# --- Clinical Versioning ---

@api.route('/Patient/<patient_id>/clinical-update', methods=['POST'])
@jwt_required()
def update_clinical_data(patient_id):
    current_username = get_jwt_identity()
    user = user_model.find_by_username(current_username)
    if not user or user.get("patientId") != patient_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    new_conditions = data.get('conditions', [])
    new_vitals = data.get('vitals', {})
    new_medications = data.get('medications', [])
    
    # 1. Inactivate existing entries (FHIR style: markers for history)
    condition_model.update_many({"subject.reference": f"Patient/{patient_id}"}, {"clinicalStatus.text": "Inactive"})
    observation_model.update_many({"subject.reference": f"Patient/{patient_id}"}, {"status": "preliminary"}) # mark old as preliminary

    from utils.validation import sanitize_text
    
    # 2. Add New Conditions
    ALLOWED_CONDITIONS = [
        "Hypertension", "Diabetes mellitus", "Asthma", "Acute upper respiratory infection",
        "Fever", "Cough", "Headache", "Coronary heart disease"
    ]
    for c_text in new_conditions:
        clean_text = sanitize_text(c_text)
        if clean_text and clean_text in ALLOWED_CONDITIONS:
            c_data = {
                "resourceType": "Condition",
                "clinicalStatus": {"text": "Active"},
                "code": {"text": clean_text},
                "subject": {"reference": f"Patient/{patient_id}"}
            }
            val_c, err = validate_fhir_resource("Condition", c_data)
            if not err: condition_model.create(val_c)

    # 3. Add New Vitals
    VITAL_MAP = {
        "systolic": {"code": "8480-6", "display": "Systolic blood pressure", "unit": "mmHg"},
        "diastolic": {"code": "8462-4", "display": "Diastolic blood pressure", "unit": "mmHg"},
        "heartRate": {"code": "8867-4", "display": "Heart rate", "unit": "beats/min"},
        "weight": {"code": "29463-7", "display": "Body Weight", "unit": "kg"},
        "height": {"code": "8302-2", "display": "Body Height", "unit": "cm"}
    }
    for key, val in new_vitals.items():
        if val and key in VITAL_MAP:
            o_data = {
                "resourceType": "Observation",
                "status": "final",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": VITAL_MAP[key]["code"], "display": VITAL_MAP[key]["display"]}]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "valueQuantity": {
                    "value": float(val),
                    "unit": VITAL_MAP[key]["unit"]
                }
            }
            val_o, err = validate_fhir_resource("Observation", o_data)
            if not err: observation_model.create(val_o)

    # 3.5 Add New Extra Observations
    extras = new_vitals.get('extras', [])
    for obs in extras:
        obs_name = sanitize_text(obs.get('name'))
        obs_value = obs.get('value')
        obs_unit = obs.get('unit')
        
        if obs_name and obs_value:
            try:
                val_num = float(obs_value)
            except:
                continue
                
            o_data = {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": obs_name},
                "subject": {"reference": f"Patient/{patient_id}"},
                "valueQuantity": {
                    "value": val_num,
                    "unit": obs_unit,
                    "system": "http://unitsofmeasure.org",
                    "code": obs_unit
                },
                "effectiveDateTime": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            val_o, err = validate_fhir_resource("Observation", o_data)
            if not err: observation_model.create(val_o)

    # 4. Create New Clinical Version Snapshot
    latest = version_model.get_latest(patient_id)
    next_version = (latest.get("versionNum", 0) + 1) if latest else 1
    version_model.create(patient_id, new_conditions, new_vitals, next_version, medications=new_medications)

    return jsonify({"message": f"Clinical data updated to Version {next_version}", "version": next_version}), 200

@api.route('/Patient/<patient_id>/clinical-history', methods=['GET'])
@jwt_required()
def get_clinical_history(patient_id):
    history = version_model.get_history(patient_id)
    # Format IDs
    for item in history:
        item["id"] = str(item["_id"])
        del item["_id"]
    return jsonify(history), 200

# --- Generic Resources ---
from models.consent_model import ConsentModel
from models.coverage_model import CoverageModel

consent_model = ConsentModel()
coverage_model = CoverageModel()

@api.route('/Consent', methods=['POST'])
@jwt_required()
def consent_resource():
    data = request.json
    # Basic Validation
    if data.get("resourceType") != "Consent":
        return jsonify({"error": "Invalid ResourceType"}), 400
    
    # Check if patient exists in reference
    # For now direct insert
    inserted_id = consent_model.create(data)
    return jsonify({"id": str(inserted_id)}), 201

@api.route('/Coverage', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def coverage_resource():
    if request.method == 'GET':
        patient_id = request.args.get('patient')
        if not patient_id: return jsonify([])
        items = coverage_model.find_by_patient(patient_id)
        return jsonify([format_id(i) for i in items])
        
    if request.method == 'POST':
        data = request.json
        if data.get("resourceType") != "Coverage":
            return jsonify({"error": "Invalid ResourceType"}), 400
        inserted_id = coverage_model.create(data)
        return jsonify({"id": str(inserted_id)}), 201

    if request.method == 'PUT':
        coverage_id = request.args.get('id')
        if not coverage_id:
            return jsonify({"error": "ID is required"}), 400
        data = request.json
        if coverage_model.update(coverage_id, data):
            return jsonify({"message": "Coverage updated"}), 200
        return jsonify({"error": "Update failed"}), 404

    if request.method == 'DELETE':
        coverage_id = request.args.get('id')
        if not coverage_id:
            return jsonify({"error": "ID is required"}), 400
        if coverage_model.delete(coverage_id):
            return jsonify({"message": "Coverage deleted"}), 200
        return jsonify({"error": "Delete failed"}), 404


# --- Analytics & Recommendations ---
@api.route('/stats/trends', methods=['GET'])
@jwt_required()
def get_trends():
    from config import db
    
    location = request.args.get('location')
    age_min = request.args.get('age_min')
    age_max = request.args.get('age_max')
    
    # Base match stage
    match_stage = {}
    
    # Advanced Filtering: Location AND Age
    valid_patient_ids = []
    
    if location or age_min or age_max:
        # Build query for patients
        query = {}
        if location:
             query["address.text"] = {"$regex": location, "$options": "i"}
             
        # Fetch matching patients to filter by ID (and check Age in Python)
        patients = list(db.get_db().patients.find(query))
        
        filtered_patients = []
        import datetime
        now = datetime.datetime.now()
        
        for p in patients:
            is_valid = True
            bdate = p.get("birthDate")
            
            # Age Check
            if (age_min or age_max) and bdate:
                try:
                    dob = None
                    if isinstance(bdate, str):
                        # Handle YYYY-MM-DD
                        dob = datetime.datetime.strptime(bdate, "%Y-%m-%d")
                    elif isinstance(bdate, (datetime.date, datetime.datetime)):
                        dob = bdate
                        # Ensure it's datetime for subtraction if it's just date
                        if isinstance(dob, datetime.date) and not isinstance(dob, datetime.datetime):
                             dob = datetime.datetime.combine(dob, datetime.datetime.min.time())
                    
                    if dob:
                        age = (now - dob).days // 365
                        if age_min and age < int(age_min): is_valid = False
                        if age_max and age > int(age_max): is_valid = False
                except Exception as e:
                    # Log error if needed, but for now just exclude
                    is_valid = False 
            
            if is_valid:
                filtered_patients.append(p)
                
        # Collect IDs for the Condition Aggregation
        valid_patient_ids = [str(p["_id"]) for p in filtered_patients] + [p.get("id") for p in filtered_patients if p.get("id")]
        
        # If filters are active but no patients match, return empty
        if not valid_patient_ids:
             return jsonify({"top_conditions": [], "patient_demographics": []})
             
        # Add filter to Condition aggregation
        match_stage = {"subject.reference": {"$in": [f"Patient/{pid}" for pid in valid_patient_ids]}}

    # 1. Condition Prevalence (Filtered)
    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$group": {"_id": "$code.text", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ])
    
    top_conditions = list(db.get_db().conditions.aggregate(pipeline))
    
    # 2. Patients by Gender (Filtered)
    # We already have filtered_patients list from above block if filters applied
    # Getting gender stats from that list is easier/safer than re-querying
    
    if location or age_min or age_max:
        # Use Python list aggregation
        from collections import Counter
        gender_counts = Counter(p.get("gender", "unknown") for p in filtered_patients)
        gender_stats = [{"_id": k, "count": v} for k, v in gender_counts.items()]
    else:
        # Full scan
        gender_stats = list(db.get_db().patients.aggregate([
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]))

    # 3. Total Conditions Count (Filtered)
    total_conditions_count = db.get_db().conditions.count_documents(match_stage)

    return jsonify({
        "top_conditions": [{"name": i["_id"], "value": i["count"]} for i in top_conditions],
        "patient_demographics": [{"name": i["_id"], "value": i["count"]} for i in gender_stats],
        "total_conditions_count": total_conditions_count
    })

@api.route('/stats/disease-trends-by-age', methods=['GET'])
@jwt_required()
def get_disease_trends_by_age():
    # Simplified logic (same as before but protected)
    from config import db
    import datetime
    
    conditions = list(db.get_db().conditions.find())
    patients = {str(p["_id"]): p for p in db.get_db().patients.find()}
    patients_by_custom_id = {p.get("id"): p for p in patients.values()}
    
    age_groups = {"0-18": {}, "19-35": {}, "36-60": {}, "60+": {}}
    
    for c in conditions:
        subject_ref = c.get("subject", {}).get("reference", "")
        p_id = subject_ref.replace("Patient/", "")
        patient = patients_by_custom_id.get(p_id) or patients.get(p_id)
        
        if patient and "birthDate" in patient:
            try:
                dob = datetime.datetime.strptime(patient["birthDate"], "%Y-%m-%d")
                age = (datetime.datetime.now() - dob).days // 365
                group = "60+"
                if age <= 18: group = "0-18"
                elif age <= 35: group = "19-35"
                elif age <= 60: group = "36-60"
                
                cond_name = c.get("code", {}).get("text", "Unknown")
                age_groups[group][cond_name] = age_groups[group].get(cond_name, 0) + 1
            except: pass

    result = []
    for group, counts in age_groups.items():
        top_disease = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
        result.append({"age_group": group, "top_diseases": [{"name": k, "value": v} for k, v in top_disease]})
        
    return jsonify(result)

@api.route('/Patient/<id>/similar', methods=['GET'])
@jwt_required()
def get_similar_patients(id):
    from services.recommendation_service import find_similar_patients
    cohort = find_similar_patients(id)
    return jsonify(cohort)

@api.route('/recommendation/<patient_id>', methods=['POST'])
@jwt_required()
def get_recommendation(patient_id):
    # Check Consent
    consent = consent_model.find_by_patient(patient_id)
    if not consent or consent.get("status") != "active":
        return jsonify({"error": "Patient consent required for analysis"}), 403

    from services.recommendation_service import find_similar_patients
    
    conditions = condition_model.find_by_patient(patient_id)
    recommended_plan = recommend_plan(conditions)
    
    # Get similar patients for social proof/explanation
    similar_patients = find_similar_patients(patient_id)
    
    return jsonify({
        "patient_id": patient_id,
        "condition_count": len(conditions),
        "conditions": [c.get("code", {}).get("text") for c in conditions],
        "recommended_plan": recommended_plan,
        "similar_cohort_size": len(similar_patients),
        "similar_patients_preview": [p["name"] for p in similar_patients],
        "all_plans": get_all_plans()
    })


@api.route('/Patient/<id>/risk', methods=['GET'])
@jwt_required()
def get_patient_risk(id):
    # Fix 404: Try multiple ID formats
    patient = patient_model.find_by_id(id)
    if not patient:
        # Fallback to direct MongoDB search if model fails
        from config import db
        from bson import ObjectId
        try:
             # Try as ObjectId without resourceType filter if it was missing
             patient = db.get_db().patients.find_one({"_id": ObjectId(id)})
        except:
             pass
             
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
        
    conditions = condition_model.find_by_patient(id)
    risk_assessment = calculate_risk_score(patient, conditions)
    
    # Extract score and label from FHIR resource for frontend display
    prediction = risk_assessment.get("prediction", [{}])[0]
    score = prediction.get("probabilityDecimal", 0)
    label = prediction.get("qualitativeRisk", {}).get("coding", [{}])[0].get("display", "Unknown")
    
    return jsonify({
        "patientId": id,
        "risk_score": score,
        "risk_label": label,
        "risk_assessment_id": risk_assessment.get("id")
    })

@api.route('/Patient/<id>/risk-simulate', methods=['POST'])
@jwt_required()
def simulate_patient_risk(id):
    patient = patient_model.find_by_id(id)
    if not patient:
        from config import db
        from bson import ObjectId
        try:
            patient = db.get_db().patients.find_one({"_id": ObjectId(id)})
        except: pass
        
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
        
    data = request.json
    weights = data.get('weights')
    
    if not weights:
        return jsonify({"error": "Weights are required for simulation"}), 400
        
    conditions = condition_model.find_by_patient(id)
    # Simulator returns the calculation but DOES NOT save to DB (handled in risk_service)
    risk_assessment = calculate_risk_score(patient, conditions, weights=weights)
    
    prediction = risk_assessment.get("prediction", [{}])[0]
    score = prediction.get("probabilityDecimal", 0)
    label = prediction.get("qualitativeRisk", {}).get("coding", [{}])[0].get("display", "Unknown")
    
    return jsonify({
        "patientId": id,
        "risk_score": score,
        "risk_label": label,
        "details": risk_assessment.get("note", [{}])[0].get("text", "")
    })
