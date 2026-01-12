from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.insurance_plan_model import InsurancePlanModel
from models.models import PatientModel, UserModel
from config import db
from utils.logger import logger

admin_bp = Blueprint('admin', __name__)
plan_model = InsurancePlanModel()
patient_model = PatientModel()

def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True

# --- Insurance Plan CRUD ---

@admin_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    # Publicly accessible for now, or restrict if needed. 
    # But usually users need to see plans to select them.
    # However, modification is admin only.
    plans = plan_model.find_all()
    for p in plans:
        p['id'] = str(p['_id'])
        del p['_id']
    return jsonify(plans)

@admin_bp.route('/plans', methods=['POST'])
@jwt_required()
def create_plan():
    claims = get_jwt()
    # Manual check since we don't have a decorator yet
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.json
    try:
        new_id = plan_model.create(data)
        logger.info(f"Admin {get_jwt_identity()} created plan: {data.get('name')} (ID: {new_id})")
        return jsonify({"id": str(new_id), "message": "Plan created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/plans/<plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.json
    if plan_model.update(plan_id, data):
        logger.info(f"Admin {get_jwt_identity()} updated plan {plan_id}")
        return jsonify({"message": "Plan updated successfully"}), 200
    return jsonify({"error": "Plan not found or update failed"}), 404

@admin_bp.route('/plans/<plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    if plan_model.delete(plan_id):
        logger.warning(f"Admin {get_jwt_identity()} deleted plan {plan_id}")
        return jsonify({"message": "Plan deleted successfully"}), 200
    return jsonify({"error": "Plan not found"}), 404

# --- Patient Read-Only View ---

@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_all_patients():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
        
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 15))
    search = request.args.get('search', None)
    
    patients, total_count = patient_model.find_paginated(page, limit, search)
    
    # Format for listing
    result = []
    for p in patients:
        p_id = p.get("id") or str(p["_id"])
        
        # Name fallback logic
        name_obj = p.get('name', [{}])[0]
        given = name_obj.get('given', [])
        family = name_obj.get('family', '')
        name_text = name_obj.get('text', '')
        
        display_name = f"{' '.join(given)} {family}".strip()
        if not display_name:
            display_name = name_text or "Unknown"

        result.append({
            "id": p_id,
            "name": display_name,
            "gender": p.get("gender"),
            "birthDate": p.get("birthDate"),
            "address": p.get("address", [{}])[0].get("text", "")
        })
        
    return jsonify({
        "data": result,
        "total": total_count,
        "page": page,
        "total_pages": (total_count + limit - 1) // limit
    })

# --- Analytics / Logs (Placeholder) ---

@admin_bp.route('/system/logs', methods=['GET'])
@jwt_required()
def get_logs():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
        
    # Mock logs
    logs = [
        {"timestamp": "2024-01-20T10:00:00Z", "level": "INFO", "message": "System started"},
        {"timestamp": "2024-01-20T10:05:00Z", "level": "INFO", "message": "DB Connection established"},
        {"timestamp": "2024-01-20T14:30:00Z", "level": "WARN", "message": "High latency detected in recommendation service"}
    ]
    return jsonify(logs)

# --- New Admin Endpoints for Redesign ---

@admin_bp.route('/stats/risk-distribution', methods=['GET'])
@jwt_required()
def get_risk_distribution():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    # Calculate risk for all patients (This could be slow for many patients, optimize later)
    # For a demo/hackathon, calculating on fly is okay, or we could cache it.
    
    from services.risk_service import calculate_risk_score
    from models.models import ConditionModel
    condition_model = ConditionModel()
    
    patients = patient_model.find_all()
    distribution = {"Low": 0, "Medium": 0, "High": 0, "Unknown": 0}
    
    for p in patients:
        # Use FHIR ID primarily, fallback to MongoDB _id
        p_id = p.get("id") or str(p["_id"])
        conditions = condition_model.find_by_patient(p_id)
        
        try:
             risk_res = calculate_risk_score(p, conditions)
             # Extract label
             prediction = risk_res.get("prediction", [{}])[0]
             label = prediction.get("qualitativeRisk", {}).get("coding", [{}])[0].get("display", "Unknown")
             
             if label in distribution:
                 distribution[label] += 1
             else:
                 distribution["Unknown"] += 1
        except Exception as e:
             print(f"Error calculating risk for patient {p_id}: {str(e)}")
             distribution["Unknown"] += 1
             
    # Format for chart (ChartJS usually takes labels and data arrays)
    return jsonify({
        "labels": ["Low Risk", "Medium Risk", "High Risk", "Unknown/Error"],
        "data": [distribution["Low"], distribution["Medium"], distribution["High"], distribution["Unknown"]]
    })

@admin_bp.route('/patients/<patient_id>/fhir', methods=['GET'])
@jwt_required()
def get_patient_fhir(patient_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    patient = patient_model.find_by_id(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
        
    # Construct a Bundle
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }
    
    # Add Patient
    p_res = patient.copy()
    p_res["id"] = str(p_res["_id"])
    del p_res["_id"]
    bundle["entry"].append({"resource": p_res})
    
    # Add Conditions
    from models.models import ConditionModel, MedicationModel, ObservationModel
    cond_model = ConditionModel()
    med_model = MedicationModel()
    obs_model = ObservationModel()
    
    conditions = cond_model.find_by_patient(patient_id)
    for c in conditions:
        c["id"] = str(c["_id"])
        del c["_id"]
        bundle["entry"].append({"resource": c})
        
    # Add Medications
    meds = med_model.find_by_patient(patient_id)
    for m in meds:
        m["id"] = str(m["_id"])
        del m["_id"]
        bundle["entry"].append({"resource": m})

    # Add Observations
    observations = obs_model.find_by_patient(patient_id)
    for o in observations:
        o["id"] = str(o["_id"])
        del o["_id"]
        bundle["entry"].append({"resource": o})
        
    return jsonify(bundle)

@admin_bp.route('/patients/<patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
        
    if patient_model.delete(patient_id):
        return jsonify({"message": "Patient deleted successfully"}), 200
    return jsonify({"error": "Patient not found"}), 404

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 15))
    search = request.args.get('search', None)
    
    from models.models import UserModel
    user_model = UserModel()
    users, total_count = user_model.find_paginated(page, limit, search)
    
    result = []
    for user in users:
        user_data = {
            "id": str(user["_id"]),
            "username": user.get("username"),
            "name": user.get("name"),
            "role": user.get("role"),
            "patientId": user.get("patientId"),
            "insurancePlan": user.get("insurancePlan"),
            "email": user.get("email")
        }
        result.append(user_data)
    
    return jsonify({
        "data": result,
        "total": total_count,
        "page": page,
        "total_pages": (total_count + limit - 1) // limit
    })

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.models import UserModel
    user_model = UserModel()
    
    # Get the current user's ID from the database using their username (JWT identity)
    current_username = get_jwt_identity()
    current_user = user_model.find_by_username(current_username)
    if current_user and str(current_user["_id"]) == user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    if user_model.delete(user_id):
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404

# --- New Admin Endpoints for Enhanced Dashboard ---

@admin_bp.route('/clinical/conditions', methods=['GET'])
@jwt_required()
def get_all_conditions():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.models import ConditionModel
    model = ConditionModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/clinical/observations', methods=['GET'])
@jwt_required()
def get_all_observations():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.models import ObservationModel
    model = ObservationModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/clinical/medications', methods=['GET'])
@jwt_required()
def get_all_medications():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.models import MedicationModel
    model = MedicationModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/clinical/risk-assessments', methods=['GET'])
@jwt_required()
def get_all_risk_assessments():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.risk_assessment_model import RiskAssessmentModel
    model = RiskAssessmentModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/insurance/coverage', methods=['GET'])
@jwt_required()
def get_all_coverage():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.coverage_model import CoverageModel
    model = CoverageModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/insurance/consents', methods=['GET'])
@jwt_required()
def get_all_consents():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    from models.consent_model import ConsentModel
    model = ConsentModel()
    data = model.find_all()
    for item in data:
        item['id'] = str(item['_id'])
        del item['_id']
    return jsonify(data)

@admin_bp.route('/system/logs', methods=['GET'])
@jwt_required()
def get_system_logs():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    log_path = os.path.join(os.path.dirname(__file__), '..', 'backend.log')
    try:
        if not os.path.exists(log_path):
            return jsonify([])
        
        with open(log_path, 'r') as f:
            # Read last 100 lines for efficiency
            lines = f.readlines()
            last_lines = lines[-100:] if len(lines) > 100 else lines
            
        logs = []
        for line in last_lines:
            # Simple parsing: [2026-01-12 13:02:53,047] WARNING in api_controller: ...
            if line.startswith('['):
                try:
                    parts = line.split('] ', 1)
                    timestamp = parts[0][1:]
                    rest = parts[1].split(' in ', 1)
                    level = rest[0]
                    module_msg = rest[1].split(': ', 1)
                    module = module_msg[0]
                    message = module_msg[1].strip()
                    
                    logs.append({
                        "timestamp": timestamp,
                        "level": level,
                        "module": module,
                        "message": message
                    })
                except:
                    logs.append({"raw": line.strip()})
            else:
                if logs and "raw" not in logs[-1]:
                    logs[-1]["message"] += f"\n{line.strip()}"
                else:
                    logs.append({"raw": line.strip()})
                    
        return jsonify(logs[::-1]) # Return newest first
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({"error": str(e)}), 500
