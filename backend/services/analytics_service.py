from models.models import PatientModel, ConditionModel, ObservationModel, MedicationModel
from datetime import datetime

class AnalyticsService:
    def __init__(self):
        self.patient_model = PatientModel()
        self.condition_model = ConditionModel()
        self.observation_model = ObservationModel()
        self.medication_model = MedicationModel()

    def _calculate_age(self, dob_str):
        if not dob_str:
            return None
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            return (datetime.now() - dob).days // 365
        except:
            return None

    def _get_age_group(self, age):
        if age is None: return "Unknown"
        if age <= 18: return "0-18"
        if age <= 30: return "19-30"
        if age <= 45: return "31-45"
        if age <= 60: return "46-60"
        return ">60"

    def get_disease_distribution(self):
        """
        1) Disease Distribution Analytics (Population Level)
        - Group all condition records by disease name
        - Count number of patients per disease
        """
        conditions = self.condition_model.find_all()
        distribution = {}
        
        for condition in conditions:
            # Check for active status if available, optionally. 
            # Requirement says "Group all condition records", but usually active is implied.
            # We'll include all for now or filter by active if clear. Let's stick to simple grouping.
            
            code_text = condition.get("code", {}).get("text", "Unknown Condition")
            distribution[code_text] = distribution.get(code_text, 0) + 1
            
        return [{"disease": k, "count": v} for k, v in distribution.items()]

    def get_disease_trends_by_age(self):
        """
        2) Disease Trends by Age Group
        - Create age buckets: 0–18, 19–30, 31–45, 46–60, >60
        - Map patient age to conditions
        - Group by disease + age group
        """
        conditions = self.condition_model.find_all()
        # Cache patients to avoid N+1 DB calls if possible, or fetch as needed.
        # For this scale, finding by ID is okay, or fetching all patients once.
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p
        
        data = {} # (Disease, AgeGroup) -> Count
        
        for condition in conditions:
            subject_ref = condition.get("subject", {}).get("reference", "")
            patient_id = subject_ref.split("/")[-1] if "/" in subject_ref else subject_ref
            
            patient = patients.get(patient_id)
            if not patient: continue
            
            age = self._calculate_age(patient.get("birthDate"))
            age_group = self._get_age_group(age)
            disease = condition.get("code", {}).get("text", "Unknown")
            
            key = (disease, age_group)
            data[key] = data.get(key, 0) + 1
            
        # Format output
        result = []
        for (disease, age_group), count in data.items():
            result.append({
                "disease": disease,
                "age_group": age_group,
                "count": count
            })
        return result

    def get_disease_trends_by_location(self):
        """
        3) Disease Trends by Location
        - Extract city from patient_profiles
        - Map diseases to patient city
        - Group by disease + location
        """
        conditions = self.condition_model.find_all()
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p
        
        data = {} # (Disease, City) -> Count
        
        for condition in conditions:
            subject_ref = condition.get("subject", {}).get("reference", "")
            patient_id = subject_ref.split("/")[-1]
            
            patient = patients.get(patient_id)
            if not patient: continue
            
            # Assuming address is a list and we take the first one's city
            city = "Unknown"
            if "address" in patient and len(patient["address"]) > 0:
                city = patient["address"][0].get("city", "Unknown")
            
            disease = condition.get("code", {}).get("text", "Unknown")
            key = (disease, city)
            data[key] = data.get(key, 0) + 1
            
        return [{"disease": d, "location": l, "count": c} for (d, l), c in data.items()]

    def get_vital_analytics(self):
        """
        4) Observation / Vital Analytics
        - Define thresholds: BP > 140 → High BP, Sugar > 180 → High Sugar
        - Classify observations as NORMAL or HIGH
        - Aggregate abnormal vitals by age group and disease
        NOTE: Linking to disease is complex if not explicitly linked in FHIR. 
        We will aggregate by Age Group as primarily requested, and maybe primary condition if easy.
        For "Aggregate abnormal vitals by age group AND disease":
        We need to see what diseases the patient has. A patient might have multiple.
        We will attribute the abnormal vital to ALL active diseases the patient has, or just Count by Age Group if disease is ambiguous.
        Let's do: Count of Abnormal Vitals by Age Group.
        """
        observations = self.observation_model.find_all()
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p
        
        abnormal_counts = {} # (VitalType, AgeGroup) -> Count
        
        for obs in observations:
            code_text = obs.get("code", {}).get("text", "").lower()
            value = obs.get("valueQuantity", {}).get("value")
            if value is None: continue
            
            is_abnormal = False
            vital_type = "Unknown"
            
            # Simple substring matching for types
            if "blood pressure" in code_text or "systolic" in code_text:
                vital_type = "High BP"
                if value > 140: is_abnormal = True
            elif "glucose" in code_text or "sugar" in code_text:
                vital_type = "High Sugar"
                if value > 180: is_abnormal = True
                
            if is_abnormal:
                subject_ref = obs.get("subject", {}).get("reference", "")
                patient_id = subject_ref.split("/")[-1]
                patient = patients.get(patient_id)
                if not patient: continue
                
                age = self._calculate_age(patient.get("birthDate"))
                age_group = self._get_age_group(age)
                
                key = (vital_type, age_group)
                abnormal_counts[key] = abnormal_counts.get(key, 0) + 1
                
        return [{"vital": v, "age_group": a, "count": c} for (v, a), c in abnormal_counts.items()]

    def _get_medication_name(self, med):
        """Robustly extract medication name from various possible FHIR fields."""
        # 1. medicationCodeableConcept.text
        name = med.get("medicationCodeableConcept", {}).get("text")
        if name: return name
        
        # 2. code.text (found in some simplified/custom records)
        name = med.get("code", {}).get("text")
        if name: return name
        
        # 3. medicationCodeableConcept.coding[0].display
        coding = med.get("medicationCodeableConcept", {}).get("coding", [])
        if coding and isinstance(coding, list) and len(coding) > 0:
            name = coding[0].get("display")
            if name: return name
            
        # 4. medicationReference.display (if linked to a Medication resource)
        name = med.get("medicationReference", {}).get("display")
        if name: return name
        
        return "Unknown Med"

    def get_medication_analytics(self):
        """
        5) Medication Analytics
        - Analyze: Medication vs disease, Medication vs age group, and unique usage
        """
        medications = self.medication_model.find_all()
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p

        conditions_map = {} # PatientID -> List of Condition Names
        all_conditions = self.condition_model.find_all()
        
        for c in all_conditions:
            subject_ref = c.get("subject", {}).get("reference", "")
            if not subject_ref: continue
            pid = subject_ref.split("/")[-1]
            c_name = c.get("code", {}).get("text", "Unknown")
            if pid not in conditions_map: conditions_map[pid] = []
            if c_name not in conditions_map[pid]:
                conditions_map[pid].append(c_name)
            
        med_vs_age = {} # (Medication, AgeGroup) -> Count
        med_vs_disease = {} # (Medication, Disease) -> Count
        usage_counts = {} # Medication -> Set of PatientIDs (for unique usage)
        
        for med in medications:
            med_name = self._get_medication_name(med)
            subject_ref = med.get("subject", {}).get("reference", "")
            if not subject_ref: continue
            pid = subject_ref.split("/")[-1]
            
            patient = patients.get(pid)
            if not patient: continue
            
            # Age Group Analysis
            age = self._calculate_age(patient.get("birthDate"))
            age_group = self._get_age_group(age)
            k1 = (med_name, age_group)
            med_vs_age[k1] = med_vs_age.get(k1, 0) + 1
            
            # Unique usage (Total Patients per Medication)
            if med_name not in usage_counts: usage_counts[med_name] = set()
            usage_counts[med_name].add(pid)
            
            # Disease Analysis (associating med with all patient conditions as proxy)
            p_conditions = conditions_map.get(pid, ["Unknown / Prophylactic"])
            for cond in p_conditions:
                k2 = (med_name, cond)
                med_vs_disease[k2] = med_vs_disease.get(k2, 0) + 1
                
        return {
            "by_age": [{"medication": m, "age_group": a, "count": c} for (m, a), c in med_vs_age.items()],
            "by_disease": [{"medication": m, "disease": d, "count": c} for (m, d), c in med_vs_disease.items()],
            "unique_usage": [{"medication": m, "count": len(pids)} for m, pids in usage_counts.items()]
        }

    def get_chronic_vs_acute_analytics(self):
        """
        8) Chronic vs Acute
        """
        CHRONIC_LIST = ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "Arthritis"]
        ACUTE_LIST = ["Cold", "Fever", "Infection", "Flu", "Fracture"]
        
        conditions = self.condition_model.find_all()
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p
        
        data = {} # (Type, AgeGroup) -> Count
        
        for c in conditions:
            name = c.get("code", {}).get("text", "")
            c_type = "Other"
            if any(chronic in name for chronic in CHRONIC_LIST):
                c_type = "Chronic"
            elif any(acute in name for acute in ACUTE_LIST):
                c_type = "Acute"
                
            subject_ref = c.get("subject", {}).get("reference", "")
            pid = subject_ref.split("/")[-1]
            patient = patients.get(pid)
            if not patient: continue
            
            age = self._calculate_age(patient.get("birthDate"))
            age_group = self._get_age_group(age)
            
            key = (c_type, age_group)
            data[key] = data.get(key, 0) + 1
            
        return [{"type": t, "age_group": a, "count": c} for (t, a), c in data.items()]
    
    def get_comorbidity_analytics(self):
        """
        9) Comorbidity Analytics
        - Count number of active conditions per patient
        - Classify: Single-condition, Multi-condition
        """
        conditions = self.condition_model.find_all()
        patients = {}
        for p in self.patient_model.find_all():
            patients[str(p["_id"])] = p
            if "id" in p:
                patients[p["id"]] = p
        
        patient_counts = {} # Pid -> Count
        for c in conditions:
            subject_ref = c.get("subject", {}).get("reference", "")
            pid = subject_ref.split("/")[-1]
            patient_counts[pid] = patient_counts.get(pid, 0) + 1
            
        results = {} # (Category, AgeGroup) -> Count
        
        for pid, count in patient_counts.items():
            category = "Multi-condition" if count > 1 else "Single-condition"
            
            patient = patients.get(pid)
            if not patient: continue
            age = self._calculate_age(patient.get("birthDate"))
            age_group = self._get_age_group(age)
            
            key = (category, age_group)
            results[key] = results.get(key, 0) + 1
            
        return [{"category": cat, "age_group": ag, "count": c} for (cat, ag), c in results.items()]
