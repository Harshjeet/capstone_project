# System Architecture: HealthAI Platform

This document provides a deep dive into the technical architecture, data flow, and core logic of the HealthAI platform.

## 🏗️ High-Level Overview

The HealthAI platform is a full-stack, FHIR-native healthcare application designed for interoperability, predictive analytics, and personalized insurance recommendations.

```mermaid
graph TD
    Client[React Frontend] <--> API[Flask REST API]
    API <--> Services[Business Logic Layer]
    Services <--> Models[FHIR Model Layer]
    Models <--> DB[(MongoDB)]
    API -- Auth -- JWT[JWT & RBAC]
```

---

## 💻 Technical Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React, Vite | Reactive UI, Component-based architecture. |
| **Styling** | Vanilla CSS, Lucide Icons | Premium aesthetic, custom design tokens. |
| **Backend** | Flask (Python) | Lightweight, modular RESTful API. |
| **Database** | MongoDB | Document-oriented storage for complex FHIR JSON. |
| **Data Standard** | HL7 FHIR (R4/R5) | Global standard for health data interoperability. |
| **Security** | Flask-JWT-Extended | Stateless authentication with Role-Based Access. |

---

## 📁 Project Structure (Backend)

The backend follows a **Modular Monolith** pattern, separating concerns into Controllers, Services, and Models.

- **`/controllers`**: HTTP entry points. Handles request parsing and response formatting.
    - `api_controller.py`: Core patient and clinical routes.
    - `admin_controller.py`: User management and directory services.
    - `analytics_controller.py`: Population-level statistics.
- **`/services`**: The "Brain" of the app. Infrastructure-independent logic.
    - `risk_service.py`: Computes risk scores based on FHIR observations and conditions.
    - `recommendation_service.py`: Similarity-based insurance matching.
    - `analytics_service.py`: Data aggregation for population health.
- **`/models`**: Data Access Objects (DAO). Interacts with MongoDB collections.
    - `models.py`: Defines standard CRUD for Patients, Observations, and Conditions.

---

## 🏥 Data Interoperability (FHIR)

Every piece of health data is stored as a native **FHIR Resource**. This ensures that the system is ready to exchange data with global hospital systems (EPIC, Cerner, etc.).

### Key Resources Used:
1.  **Patient**: Identity, demographics, and contact info.
2.  **Condition**: Clinical issues (e.g., Diabetes, Hypertension).
3.  **Observation**: Point-in-time vitals (height, weight, blood pressure).
4.  **MedicationRequest**: Prescriptions and active medical management.
5.  **RiskAssessment**: Outcomes of the risk engine.
6.  **Consent**: Patient approval for data analysis.

---

## 🔄 Core Logic Flows

### 1. The Risk Scoring Engine
The system calculates a "General Health Risk" score (0-100) by analyzing four quadrants:
- **Baseline**: Age-based risk factors.
- **Clinical**: Presence of "High Risk" items (Stroke, Cancer, Heart Disease).
- **Physiological**: Abnormal values in latest vitals (BP > 140/90).
- **Management**: Number of active medications.

### 2. Similarity-Based Recommendations
Instead of hardcoded rules, the Insurance engine uses a **Cohort Analysis**:
- It finds patients with similar demographics (age, gender, location).
- It analyzes the clinical profiles within that cohort.
- It recommends the plan that offers the best coverage statistical outcomes for that specific profile.

---

## 🔐 Security & RBAC

The system implements **Role-Based Access Control (RBAC)** to ensure privacy:

| Role | Access Level | Permissions |
| :--- | :--- | :--- |
| **Patient** | Self-Service | Can edit OWN health data, view OWN risk, and enroll in plans. |
| **Admin** | System-Wide | Can view population analytics, manage all users, and define insurance plans. |

- **Security Mechanism**: JWT (JSON Web Tokens) are used for every request. The token contains a `role` claim which the backend verifies before executing sensitive logic.

---

## 📊 Analytics Pipeline
The population health dashboard uses MongoDB **Aggregation Pipelines** to process thousands of records in real-time. This allows admins to see disease distribution and vital trends across different locations and age groups without performance lag.
