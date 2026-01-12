# HealthAI: Population Health & Insurance Intelligence

HealthAI is a comprehensive healthcare platform designed to leverage population health data for predictive risk stratification and personalized insurance recommendations. Built with FHIR-style data structures, it provides both patients and healthcare administrators with actionable insights.

## 🚀 Features

### 🏥 Patient Dashboard
- **Clinical History:** Track active and historical conditions, vitals, and medications.
- **Risk Analysis:** View personal risk scores calculated via backend intelligence services.
- **Insurance Recommendations:** Get tailored insurance plan suggestions based on health risk and demographic similarity to other patients.
- **Direct Enrollment:** Enroll in recommended plans directly from the dashboard.

### 📊 Admin Intelligence Command
- **Population Analytics:** Real-time metrics on total patients, active conditions, and abnormal vitals.
- **Risk Stratification:** Distribution of patients across Low, Medium, and High-risk tiers.
- **Therapeutic Utilization:** Analyze medication usage trends across the population.
- **Disease Demographics:** Track disease trends by age group and geographic region.
- **Plan Management:** Create and manage insurance plans.

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, Chart.js, Lucide Icons, Tailwind CSS.
- **Backend:** Python 3.13, Flask, MongoDB, Flask-JWT-Extended.
- **Data Standard:** FHIR-inspired resource structures (Patient, Condition, Observation, MedicationRequest, Coverage).

## 📥 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.13+)
- [MongoDB](https://www.mongodb.com/try/download/community) (running locally on port 27017)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   ```

### 🧬 Data Seeding

To populate the database with FHIR resources and insurance plans:
```bash
cd backend
python seed_all_data.py  # Seeds patients, conditions, observations, and medications
python seed_plans.py     # Seeds initial insurance plans
python create_admin.py    # (Optional) Create a default admin user
```

## ⚙️ Running the Application

1. **Start the Backend:**
   ```bash
   cd backend
   python app.py
   ```
   The API will be available at `http://localhost:5000`.

2. **Start the Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

## 🧪 Testing

The project includes a comprehensive suite of UAT (User Acceptance Testing) scripts using `pytest`.

To run all tests:
```bash
python3 -m pytest testing/pytest -v
```

Tests cover:
- Authentication & RBAC
- FHIR Data Ingestion
- Risk Calculation Logic
- Insurance Recommendation Engine
- Analytics Accuracy
- System Stability & Performance

## 📂 Project Structure

- `backend/`: Flask API, Services (Risk, Recommendation, Analytics), and Database Models.
- `frontend/`: React components, Pages, and Styling.
- `testing/`: Pytest suite and UAT scripts.
- `design/`: Design documentation and React-to-Figma guides.
