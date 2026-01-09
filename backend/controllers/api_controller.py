from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
from models.models import PatientModel, ConditionModel, ObservationModel, MedicationModel, UserModel
from services.recommendation_service import get_all_plans, recommend_plan
from services.risk_service import calculate_risk_score
from utils.validation import validate_fhir_resource

api = Blueprint('api', __name__)
patient_model = PatientModel()
condition_model = ConditionModel()
observation_model = ObservationModel()
medication_model = MedicationModel()
user_model = UserModel()

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
    ALLOWED_CONDITIONS = [
        "Hypertension", "Diabetes mellitus", "Asthma", "Acute upper respiratory infection",
        "Fever", "Cough", "Headache", "Coronary heart disease"
    ]
    
    for c_text in conditions:
        clean_text = sanitize_text(c_text)
        if clean_text and clean_text in ALLOWED_CONDITIONS:
            c_data = {
                "resourceType": "Condition",
                "clinicalStatus": {"text": "Active"},
                "code": {"text": clean_text},
                "subject": {"reference": f"Patient/{patient_id_str}"}
            }
            val_c, err = validate_fhir_resource("Condition", c_data)
            if not err: condition_model.create(val_c)

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
    
    # 3. Insurance (Coverage)
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
        patient_id = request.args.get('patient')
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

# --- Resources ---

@api.route('/Patient', methods=['GET', 'POST'])
@jwt_required()
def patient_resource():
    return handle_crud(patient_model, "Patient")

@api.route('/Condition', methods=['GET', 'POST'])
@jwt_required()
def condition_resource():
    return handle_crud(condition_model, "Condition")

@api.route('/Observation', methods=['GET', 'POST'])
@jwt_required()
def observation_resource():
    return handle_crud(observation_model, "Observation")

@api.route('/Medication', methods=['GET', 'POST'])
@jwt_required()
def medication_resource():
    return handle_crud(medication_model, "MedicationRequest")

# --- New Resources ---
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

@api.route('/Coverage', methods=['GET', 'POST'])
@jwt_required()
def coverage_resource():
    if request.method == 'GET':
        patient_id = request.args.get('patient')
        if not patient_id: return jsonify([])
        items = coverage_model.find_by_patient(patient_id)
        return jsonify([format_id(i) for i in items])
        
    data = request.json
    if data.get("resourceType") != "Coverage":
         return jsonify({"error": "Invalid ResourceType"}), 400
         
    inserted_id = coverage_model.create(data)
    return jsonify({"id": str(inserted_id)}), 201


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

    return jsonify({
        "top_conditions": [{"name": i["_id"], "value": i["count"]} for i in top_conditions],
        "patient_demographics": [{"name": i["_id"], "value": i["count"]} for i in gender_stats]
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
    patient = patient_model.find_by_id(id)
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
