import json
import random
from datetime import datetime, timedelta

# 1. USA DEMOGRAPHIC POOLS
female_names = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"]
male_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
usa_locations = [
    {"city": "New York", "state": "NY"}, {"city": "Los Angeles", "state": "CA"}, {"city": "Chicago", "state": "IL"},
    {"city": "Houston", "state": "TX"}, {"city": "Phoenix", "state": "AZ"}, {"city": "Philadelphia", "state": "PA"},
    {"city": "Austin", "state": "TX"}, {"city": "San Diego", "state": "CA"}, {"city": "Dallas", "state": "TX"}
]

# 2. YOUR PROVIDED DATA POOLS
conditions_pool = [
    "Type 1 Diabetes", "Type 2 Diabetes", "Prediabetes", "Metabolic Syndrome", "Hyperglycemia", "Hypoglycemia",
    "Hypothyroidism", "Hyperthyroidism", "Goiter", "Cushing Syndrome", "Addison Disease",
    "Essential Hypertension", "Secondary Hypertension", "Coronary Artery Disease", "Stable Angina", "Unstable Angina",
    "Myocardial Infarction (History)", "Heart Failure with Reduced Ejection Fraction", "Heart Failure with Preserved Ejection Fraction",
    "Atrial Fibrillation", "Atrial Flutter", "Peripheral Artery Disease", "Deep Vein Thrombosis", "Pulmonary Embolism",
    "Asthma", "Chronic Obstructive Pulmonary Disease", "Chronic Bronchitis", "Emphysema", "Obstructive Sleep Apnea",
    "Acute Bronchitis", "Pneumonia", "Chronic Kidney Disease (Stage 1)", "Chronic Kidney Disease (Stage 2)",
    "Chronic Kidney Disease (Stage 3)", "Chronic Kidney Disease (Stage 4)", "Acute Kidney Injury", "Nephrotic Syndrome",
    "Gastroesophageal Reflux Disease (GERD)", "Peptic Ulcer Disease", "Irritable Bowel Syndrome", "Inflammatory Bowel Disease",
    "Ulcerative Colitis", "Crohn Disease", "Fatty Liver Disease", "Alcoholic Liver Disease", "Hepatitis B", "Hepatitis C",
    "Migraine", "Tension Headache", "Epilepsy", "Seizure Disorder", "Parkinson Disease", "Alzheimer Disease",
    "Stroke (Ischemic)", "Stroke (Hemorrhagic)", "Peripheral Neuropathy", "Generalized Anxiety Disorder", "Major Depressive Disorder",
    "Persistent Depressive Disorder", "Bipolar Disorder Type I", "Bipolar Disorder Type II", "Schizophrenia",
    "Post-Traumatic Stress Disorder", "Insomnia", "Osteoarthritis", "Rheumatoid Arthritis", "Osteoporosis", "Fibromyalgia",
    "Chronic Low Back Pain", "Sciatica", "Gout", "Iron Deficiency Anemia", "Vitamin B12 Deficiency Anemia", "Sickle Cell Disease",
    "Thalassemia Minor", "Psoriasis", "Eczema", "Acne Vulgaris", "Cellulitis", "Chronic Ulcers", "COVID-19 (History)",
    "Tuberculosis", "HIV Infection", "Urinary Tract Infection", "Sepsis", "Polycystic Ovary Syndrome (PCOS)", "Endometriosis",
    "Benign Prostatic Hyperplasia", "Erectile Dysfunction", "Obesity", "Morbid Obesity", "Malnutrition", "Vitamin D Deficiency",
    "Smoking Dependence", "Alcohol Use Disorder"
]

# (Name, Unit, Min, Max, Decimals)
observations_pool = [
    ("Body Weight", "kg", 40, 160, 1), ("Height", "cm", 140, 200, 0), ("BMI", "kg/m2", 16.0, 50.0, 1),
    ("Heart Rate", "bpm", 45, 120, 0), ("Respiratory Rate", "breaths/min", 10, 30, 0), ("Body Temperature", "°C", 35.5, 39.5, 1),
    ("Oxygen Saturation", "%", 85, 100, 0), ("Systolic Blood Pressure", "mmHg", 90, 200, 0), ("Diastolic Blood Pressure", "mmHg", 50, 120, 0),
    ("Fasting Blood Glucose", "mg/dL", 60, 300, 0), ("Random Blood Glucose", "mg/dL", 70, 350, 0), ("HbA1c", "%", 4.0, 13.5, 1),
    ("Total Cholesterol", "mg/dL", 120, 350, 0), ("LDL Cholesterol", "mg/dL", 40, 250, 0), ("HDL Cholesterol", "mg/dL", 20, 100, 0),
    ("Triglycerides", "mg/dL", 50, 600, 0), ("Serum Creatinine", "mg/dL", 0.4, 4.5, 2), ("Blood Urea Nitrogen (BUN)", "mg/dL", 5, 80, 0),
    ("Estimated GFR", "mL/min/1.73m2", 10, 120, 0), ("Sodium", "mmol/L", 125, 150, 0), ("Potassium", "mmol/L", 2.5, 6.5, 1),
    ("Chloride", "mmol/L", 90, 115, 0), ("Calcium", "mg/dL", 7.0, 11.5, 1), ("ALT", "U/L", 5, 250, 0), ("AST", "U/L", 5, 250, 0),
    ("Alkaline Phosphatase", "U/L", 30, 300, 0), ("Total Bilirubin", "mg/dL", 0.2, 5.0, 1), ("Hemoglobin", "g/dL", 7.0, 18.5, 1),
    ("Hematocrit", "%", 20, 55, 0), ("White Blood Cell Count", "10^9/L", 2.0, 25.0, 1), ("Platelet Count", "10^3/uL", 80, 600, 0),
    ("TSH", "mIU/L", 0.01, 20.0, 2), ("Free T4", "ng/dL", 0.3, 4.5, 2), ("C-Reactive Protein", "mg/L", 0.1, 200, 1), ("ESR", "mm/hr", 1, 120, 0)
]

medications_pool = [
    "Metformin", "Insulin Glargine", "Insulin Lispro", "Glipizide", "Gliclazide", "Sitagliptin", "Empagliflozin", "Dapagliflozin",
    "Semaglutide", "Liraglutide", "Lisinopril", "Enalapril", "Losartan", "Valsartan", "Amlodipine", "Nifedipine",
    "Hydrochlorothiazide", "Chlorthalidone", "Metoprolol", "Carvedilol", "Atenolol", "Furosemide", "Spironolactone",
    "Atorvastatin", "Rosuvastatin", "Simvastatin", "Fenofibrate", "Ezetimibe", "Albuterol Inhaler", "Salbutamol",
    "Budesonide Inhaler", "Fluticasone", "Montelukast", "Omeprazole", "Pantoprazole", "Esomeprazole", "Famotidine", "Ranitidine",
    "Sertraline", "Escitalopram", "Fluoxetine", "Venlafaxine", "Duloxetine", "Amitriptyline", "Alprazolam", "Clonazepam",
    "Quetiapine", "Olanzapine", "Lithium", "Ibuprofen", "Naproxen", "Diclofenac", "Acetaminophen", "Tramadol", "Morphine",
    "Cyclobenzaprine", "Methocarbamol", "Warfarin", "Apixaban", "Rivaroxaban", "Clopidogrel", "Aspirin", "Vitamin D3",
    "Calcium Carbonate", "Iron Sulfate", "Vitamin B12", "Folic Acid", "Multivitamin", "Amoxicillin", "Azithromycin",
    "Ciprofloxacin", "Levofloxacin", "Ceftriaxone", "Doxycycline"
]

# 3. GENERATION SCRIPT
patients, all_conditions, all_observations, all_med_requests = [], [], [], []

for i in range(51, 301):
    p_id = f"p{str(i).zfill(3)}"
    gender = random.choice(["male", "female"])
    first = random.choice(female_names if gender == "female" else male_names)
    last = random.choice(last_names)
    loc = random.choice(usa_locations)
    
    # Random Birthdate (1-80 years old)
    birth_date = (datetime.now() - timedelta(days=random.randint(365, 80*365))).strftime("%Y-%m-%d")
    
    # 1. Patient Resource
    patients.append({
        "resourceType": "Patient", "id": p_id,
        "name": [{"given": [first], "family": last}],
        "gender": gender, "birthDate": birth_date,
        "address": [{"city": loc["city"], "state": loc["state"], "country": "USA"}]
    })
    
    # Randomize Counts
    num_c = random.randint(1, 6)
    num_o = random.randint(3, 12)
    num_m = random.randint(2, 10)
    
    # 2. Condition Resources (Exact Format)
    p_condition_ids = []
    selected_conditions = random.sample(conditions_pool, num_c)
    for idx, c_name in enumerate(selected_conditions):
        c_id = f"c{p_id[1:]}{idx}"
        p_condition_ids.append(c_id)
        all_conditions.append({
            "resourceType": "Condition", "id": c_id,
            "subject": {"reference": f"Patient/{p_id}"},
            "code": {
                "coding": [{"system": "http://snomed.info/sct", "code": str(random.randint(100000000, 999999999)), "display": c_name}],
                "text": c_name
            },
            "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
            "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-verstatus", "code": "confirmed"}]}
        })
        
    # 3. MedicationRequest Resources (Linked to Condition)
    selected_meds = random.sample(medications_pool, min(num_m, len(medications_pool)))
    for idx, m_name in enumerate(selected_meds):
        all_med_requests.append({
            "resourceType": "MedicationRequest", "id": f"m{p_id[1:]}{idx}",
            "status": "active", "intent": "order",
            "medicationCodeableConcept": {
                "coding": [{"system": "http://www.nlm.nih.gov/research/rxnorm", "code": str(random.randint(100000, 999999)), "display": f"{m_name} Oral Tablet"}],
                "text": f"{m_name} Oral Tablet"
            },
            "subject": {"reference": f"Patient/{p_id}"},
            "reasonReference": [{"reference": f"Condition/{random.choice(p_condition_ids)}"}],
            "dosageInstruction": [{
                "text": "As directed by physician",
                "timing": {"repeat": {"frequency": 1, "period": 1, "periodUnit": "d"}}
            }]
        })
        
    # 4. Observation Resources
    for idx in range(num_o):
        obs_meta = random.choice(observations_pool)
        name, unit, low, high, dec = obs_meta
        val = round(random.uniform(low, high), dec) if dec > 0 else int(random.uniform(low, high))
        all_observations.append({
            "resourceType": "Observation", "id": f"o{p_id[1:]}{idx}",
            "subject": {"reference": f"Patient/{p_id}"},
            "code": {"text": name},
            "valueQuantity": {"value": val, "unit": unit}
        })

# 4. SAVE TO FILES
with open('usa_fresh_patients.json', 'w') as f: json.dump(patients, f, indent=2)
with open('usa_fresh_conditions.json', 'w') as f: json.dump(all_conditions, f, indent=2)
with open('usa_fresh_observations.json', 'w') as f: json.dump(all_observations, f, indent=2)
with open('usa_fresh_medrequests.json', 'w') as f: json.dump(all_med_requests, f, indent=2)

print(f"USA Fresh FHIR Dataset generated for {len(patients)} patients.")