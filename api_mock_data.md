# HealthAI API Mock Data Guide

Use this guide to copy-paste mock data into the **Swagger UI** (`/api/docs`) for manual verification of each endpoint.

## 🔐 Authentication & Registration

### POST `/auth/login`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### POST `/auth/register`
```json
{
  "username": "manual_tester",
  "password": "password123",
  "patientDetails": {
    "firstName": "Manual",
    "lastName": "Tester",
    "gender": "female",
    "birthDate": "1988-08-08",
    "mobile": "555-9999",
    "address": "456 Swagger Lane"
  },
  "conditions": ["Hypertension"],
  "medications": ["Metformin"],
  "vitals": {
    "systolic": "120",
    "diastolic": "80",
    "heartRate": "72",
    "weight": "65",
    "height": "165"
  }
}
```

---

## 🏥 FHIR Resources

### POST `/Patient`
```json
{
  "resourceType": "Patient",
  "name": [
    {
      "text": "FHIR Manual Test"
    }
  ],
  "gender": "male",
  "birthDate": "1990-01-01"
}
```

### POST `/Condition`
> [!NOTE]
> Replace `{id}` with a valid Patient ID.
```json
{
  "resourceType": "Condition",
  "clinicalStatus": {
    "text": "Active"
  },
  "code": {
    "text": "Diabetes mellitus"
  },
  "subject": {
    "reference": "Patient/{id}"
  }
}
```

### POST `/Consent`
```json
{
  "resourceType": "Consent",
  "status": "active",
  "scope": { "text": "Research" },
  "category": [{ "text": "Privacy" }],
  "patient": { "reference": "Patient/{id}" }
}
```

---

## 🛠️ Admin Management

### POST `/admin/plans`
```json
{
  "name": "Swagger Premium",
  "provider": "Mock Health",
  "type": "Platinum",
  "description": "Premium plan for API testing verification.",
  "cost": 500
}
```

---

## 📈 Clinical Updates

### POST `/Patient/{id}/clinical-update`
```json
{
  "conditions": [
    "Asthma",
    "Coronary heart disease"
  ],
  "vitals": {
    "systolic": "135",
    "diastolic": "88",
    "heartRate": "80",
    "weight": "72"
  },
  "medications": ["Aspirin"]
}
```

---

## 🧠 Analytics & Recommendations

### POST `/recommendation/{id}`
> [!IMPORTANT]
> Requires the Patient to have an 'active' Consent record first.
```json
{}
```
*(Empty body is sufficient; logic is based on the Patient ID in the URL path)*

---

## 🔍 Data Inspection (GET)
For all **GET** endpoints listed below, no request body is needed. Simply click **"Try it out"** and **"Execute"**:
- `/registration-data`
- `/admin/patients` (Query Params: `page`, `limit`, `search`)
- `/admin/users`
- `/admin/stats/risk-distribution`
- `/analytics/population/medications`
- `/analytics/population/vitals`
- `/analytics/population/disease-distribution`
- `/Patient/{id}/clinical-history`
- `/Patient/{id}/risk`
