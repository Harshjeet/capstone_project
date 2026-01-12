from flask import Blueprint, jsonify, request
from services.analytics_service import AnalyticsService
import services.risk_service as risk_service
import services.recommendation_service as recommendation_service
from models.models import PatientModel, ConditionModel

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()
patient_model = PatientModel()
condition_model = ConditionModel()

# --- POPULATION ANALYTICS (ADMIN ONLY) ---

@analytics_bp.route('/population/disease-distribution', methods=['GET'])
def get_disease_distribution():
    # RBAC: Add admin check decorator here in real app
    data = analytics_service.get_disease_distribution()
    return jsonify(data), 200

@analytics_bp.route('/population/disease-trends-by-age', methods=['GET'])
def get_disease_trends_by_age():
    data = analytics_service.get_disease_trends_by_age()
    return jsonify(data), 200

@analytics_bp.route('/population/disease-trends-by-location', methods=['GET'])
def get_disease_trends_by_location():
    data = analytics_service.get_disease_trends_by_location()
    return jsonify(data), 200

@analytics_bp.route('/population/vitals', methods=['GET'])
def get_vital_analytics():
    data = analytics_service.get_vital_analytics()
    return jsonify(data), 200

@analytics_bp.route('/population/medications', methods=['GET'])
def get_medication_analytics():
    data = analytics_service.get_medication_analytics()
    return jsonify(data), 200

@analytics_bp.route('/population/chronic-acute', methods=['GET'])
def get_chronic_vs_acute():
    data = analytics_service.get_chronic_vs_acute_analytics()
    return jsonify(data), 200

@analytics_bp.route('/population/comorbidity', methods=['GET'])
def get_comorbidity():
    data = analytics_service.get_comorbidity_analytics()
    return jsonify(data), 200


# --- PATIENT ANALYTICS (PATIENT SELF or ADMIN) ---

@analytics_bp.route('/patient/<patient_id>/risk', methods=['GET'])
def get_patient_risk(patient_id):
    # RBAC: Verify current_user.id == patient_id (if Patient) or current_user.role == Admin
    
    # Check if patient exists
    patient = patient_model.find_by_id(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
        
    conditions = condition_model.find_by_patient(patient_id)
    
    # Calculate Risk (Recalculate on fly or fetch latest)
    # The requirement asks for "Personal risk score" visible to patient.
    # Re-calculating ensures it's fresh.
    risk_assessment = risk_service.calculate_risk_score(patient, conditions)
    
    return jsonify(risk_assessment), 200

@analytics_bp.route('/patient/<patient_id>/similarity', methods=['GET'])
def get_patient_similarity(patient_id):
    # RBAC: Similar access check
    
    # "Abstract similarity insights" + Insurance Recommendation
    # Requirement 7 says: "Generate explanation text" and recommend plan.
    # Requirement "Patient Similarity" is used FOR insurance recommendation.
    # We will expose the Insurance Recommendation which internally uses Similarity.
    # If the UI specifically needs the list of similar patients (anonymized), we can expose that too.
    # Let's Expose the "Insurance Recommendation" which includes the "explanation text" derived from similarity.
    
    recommendation = recommendation_service.get_insurance_recommendation_for_patient(patient_id)
    return jsonify(recommendation), 200
