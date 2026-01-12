import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Activity, Pill, ShieldCheck, Thermometer, User, Edit, History, X, Check, Save, Clock, ChevronRight, PlusCircle, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import ConsentModal from '../components/ConsentModal';
import MultiSelect from '../components/MultiSelect';

const PatientDashboard = () => {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [medications, setMedications] = useState([]);
    const [fullConditions, setFullConditions] = useState([]);
    const [showConsent, setShowConsent] = useState(false);
    const [consentGiven, setConsentGiven] = useState(false);
    const [activeCoverages, setActiveCoverages] = useState([]);
    const [regData, setRegData] = useState({ conditions: [], observations: [], medications: [] });

    // Edit Profile State
    const [isEditingProfile, setIsEditingProfile] = useState(false);
    const [profileForm, setProfileForm] = useState({ name: user?.name || '', address: '', phone: '' });

    // History & Version State
    const [historyData, setHistoryData] = useState([]);
    const [historyModal, setHistoryModal] = useState({ isOpen: false, title: '', type: '' });
    const [clinicalHistory, setClinicalHistory] = useState([]);
    const [isEditingClinical, setIsEditingClinical] = useState(false);
    const [clinicalForm, setClinicalForm] = useState({ conditions: [], vitals: {}, medications: [] });
    const [selectedObsToAdd, setSelectedObsToAdd] = useState('');
    const [searchTerms, setSearchTerms] = useState({ conditions: '', medications: '' });
    const [showVersionHistory, setShowVersionHistory] = useState(false);

    // Risk Simulator State
    const [weights, setWeights] = useState({
        age: 30,
        conditions: 40,
        observations: 20,
        medications: 10
    });
    const [simulatedRisk, setSimulatedRisk] = useState(null);
    const [isSimulating, setIsSimulating] = useState(false);

    const ALLOWED_CONDITIONS = [
        "Hypertension", "Diabetes mellitus", "Asthma", "Acute upper respiratory infection",
        "Fever", "Cough", "Headache", "Coronary heart disease"
    ];

    const fetchHealthData = async () => {
        if (!user?.patientId) return;
        try {
            const results = await Promise.allSettled([
                axios.post(`/recommendation/${user.patientId}`),
                axios.get(`/Medication?patient=${user.patientId}`),
                axios.get(`/Patient/${user.patientId}/risk`),
                axios.get(`/Condition?patient=${user.patientId}`),
                axios.get(`/Patient?id=${user.patientId}`),
                axios.get(`/Patient/${user.patientId}/clinical-history`),
                axios.get(`/Coverage?patient=${user.patientId}`),
                axios.get('/registration-data')
            ]);

            const [recRes, medRes, riskRes, condRes, patientRes, clinicalHistRes, covRes, regRes] = results;

            // Extract data from fulfilled promises
            const recData = recRes.status === 'fulfilled' ? recRes.value.data : null;
            const medData = medRes.status === 'fulfilled' ? medRes.value.data : [];
            const riskData = riskRes.status === 'fulfilled' ? riskRes.value.data : null;
            const condData = condRes.status === 'fulfilled' ? condRes.value.data : [];
            const patientData = patientRes.status === 'fulfilled' ? patientRes.value.data : null;

            // Consolidate data into state
            setData({
                ...(recData || {}),
                ...(riskData || {}),
                patientResource: patientData
            });
            setMedications(medData);
            setFullConditions(condData);
            setActiveCoverages(covRes.status === 'fulfilled' ? covRes.value.data.filter(c => c.status === 'active') : []);
            if (regRes.status === 'fulfilled') setRegData(regRes.value.data);

            if (clinicalHistRes.status === 'fulfilled') {
                const hist = clinicalHistRes.value.data;
                setClinicalHistory(hist);
                if (hist.length > 0) {
                    setClinicalForm({
                        conditions: hist[0].conditions || [],
                        vitals: hist[0].vitals || {},
                        medications: hist[0].medications || []
                    });
                }
            }

            if (patientData) {
                setProfileForm({
                    name: patientData.name?.[0]?.text || '',
                    address: patientData.address?.[0]?.text || '',
                    phone: patientData.telecom?.[0]?.value || ''
                });
            }

            const forbidden = results.some(r => r.status === 'rejected' && r.reason?.response?.status === 403);
            if (forbidden) {
                setShowConsent(true);
            }

        } catch (err) {
            console.error("Critical error in fetchHealthData", err);
        }
    };

    useEffect(() => {
        fetchHealthData();
    }, [user, consentGiven]);

    const handleConsent = () => {
        setConsentGiven(true);
        setShowConsent(false);
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        try {
            const updatedPatient = {
                ...data.patientResource,
                name: [{ text: profileForm.name }],
                address: [{ text: profileForm.address }],
                telecom: [{ system: 'phone', value: profileForm.phone }]
            };
            await axios.put(`/Patient?id=${user.patientId}`, updatedPatient);
            setIsEditingProfile(false);
            fetchHealthData();
            alert("Profile updated successfully!");
        } catch (err) {
            console.error("Failed to update profile", err);
            alert("Update failed");
        }
    };

    const handleUpdateClinical = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`/Patient/${user.patientId}/clinical-update`, clinicalForm);
            setIsEditingClinical(false);
            fetchHealthData();
            alert("Clinical data updated to new version!");
        } catch (err) {
            console.error("Failed to update clinical data", err);
            alert("Update failed");
        }
    };

    const fetchHistory = async (id, type, name) => {
        try {
            const res = await axios.get(`/${type}/${id}/history`);
            setHistoryData(res.data);
            setHistoryModal({ isOpen: true, title: name, type });
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    const toggleCondition = (cond) => {
        setClinicalForm(prev => {
            const current = [...(prev.conditions || [])];
            if (current.includes(cond)) {
                return { ...prev, conditions: current.filter(c => c !== cond) };
            } else {
                return { ...prev, conditions: [...current, cond] };
            }
        });
    };

    const handleExtraObsChange = (name, value) => {
        setClinicalForm(prev => ({
            ...prev,
            vitals: {
                ...prev.vitals,
                extras: (prev.vitals.extras || []).map(obs =>
                    obs.name === name ? { ...obs, value } : obs
                )
            }
        }));
    };

    const addObservation = () => {
        if (!selectedObsToAdd) return;
        const obsTemplate = regData.observations.find(o => o[0] === selectedObsToAdd);
        if (obsTemplate && !(clinicalForm.vitals.extras || []).some(o => o.name === selectedObsToAdd)) {
            setClinicalForm(prev => ({
                ...prev,
                vitals: {
                    ...prev.vitals,
                    extras: [...(prev.vitals.extras || []), {
                        name: obsTemplate[0],
                        unit: obsTemplate[1],
                        value: ''
                    }]
                }
            }));
        }
        setSelectedObsToAdd('');
    };

    const removeObservation = (name) => {
        setClinicalForm(prev => ({
            ...prev,
            vitals: {
                ...prev.vitals,
                extras: (prev.vitals.extras || []).filter(o => o.name !== name)
            }
        }));
    };

    const toggleMedication = (med) => {
        setClinicalForm(prev => {
            const current = [...(prev.medications || [])];
            if (current.includes(med)) {
                return { ...prev, medications: current.filter(m => m !== med) };
            } else {
                return { ...prev, medications: [...current, med] };
            }
        });
    };

    const handleWeightChange = (factor, value) => {
        const val = parseInt(value);
        const diff = val - weights[factor];
        const otherFactors = Object.keys(weights).filter(f => f !== factor);

        const totalOther = otherFactors.reduce((sum, f) => sum + weights[f], 0);
        const newWeights = { ...weights, [factor]: val };

        if (totalOther === 0) {
            otherFactors.forEach(f => {
                newWeights[f] = Math.max(0, Math.round(-diff / otherFactors.length));
            });
        } else {
            otherFactors.forEach(f => {
                const ratio = weights[f] / totalOther;
                newWeights[f] = Math.max(0, weights[f] - Math.round(diff * ratio));
            });
        }

        const finalSum = Object.values(newWeights).reduce((a, b) => a + b, 0);
        if (finalSum !== 100) {
            const lastFactor = otherFactors[otherFactors.length - 1];
            newWeights[lastFactor] += (100 - finalSum);
        }
        setWeights(newWeights);
    };

    const handleCancelPlan = async (coverageId) => {
        if (!window.confirm("Are you sure you want to cancel this insurance plan?")) return;
        try {
            await axios.delete(`/Coverage?id=${coverageId}`);
            fetchHealthData();
            alert("Plan cancelled successfully.");
        } catch (err) {
            console.error("Failed to cancel plan", err);
            alert("Cancellation failed.");
        }
    };

    const handleSelectPlan = async (plan) => {
        if (!user?.patientId) return;
        const isPlanActive = activeCoverages.some(c => c.class?.[0]?.value === plan.id && c.status === 'active');
        if (isPlanActive) {
            alert("You already have this plan active!");
            return;
        }

        setIsSimulating(true); // Reuse simulating state for loading
        try {
            const coverageData = {
                resourceType: "Coverage",
                status: "active",
                beneficiary: { reference: `Patient/${user.patientId}` },
                payor: [{ display: "Health Insurance Provider" }],
                class: [{
                    type: { coding: [{ system: "http://terminology.hl7.org/CodeSystem/coverage-class", code: "plan" }] },
                    value: plan.id,
                    name: plan.name
                }]
            };

            await axios.post('/Coverage', coverageData);
            alert(`Successfully enrolled in ${plan.name}!`);
            fetchHealthData();
        } catch (err) {
            console.error(err);
            alert("Enrollment failed.");
        } finally {
            setIsSimulating(false);
        }
    };

    const runSimulation = async () => {
        if (!user?.patientId) return;
        setIsSimulating(true);
        try {
            const res = await axios.post(`/Patient/${user.patientId}/risk-simulate`, { weights });
            setSimulatedRisk(res.data);
        } catch (err) {
            console.error("Simulation failed", err);
        } finally {
            setIsSimulating(false);
        }
    };


    useEffect(() => {
        const timeout = setTimeout(runSimulation, 500);
        return () => clearTimeout(timeout);
    }, [weights]);

    if (!data?.patientResource && showConsent) {
        return <ConsentModal onConsentGiven={handleConsent} />;
    }

    if (!data) return <div className="loading">Loading your health profile...</div>;

    const { recommended_plan } = data;

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <h1>My Health Overview</h1>
                        <p>Personalized insights • Profile Version: {clinicalHistory.length || 1}</p>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                        {(simulatedRisk?.risk_label || data?.risk_label) ? (
                            <div className={`risk-badge risk-${(simulatedRisk?.risk_label || data.risk_label).toLowerCase()}`}>
                                Risk Level: {simulatedRisk?.risk_label || data.risk_label} (Score: {simulatedRisk?.risk_score || data.risk_score})
                            </div>
                        ) : (
                            <div className="risk-badge risk-unknown">Risk Level: Not Calculated</div>
                        )}
                        <button onClick={() => setShowVersionHistory(true)} className="btn-text" style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <History size={14} /> View Version History
                        </button>
                    </div>
                </div>
            </header>

            <div className="stats-grid patient-grid">

                {/* Risk Analysis Tool */}
                <div className="card full-width" style={{ borderLeft: '4px solid var(--primary)' }}>
                    <div className="card-header" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <Activity className="icon" size={24} style={{ color: 'var(--primary)' }} />
                        <div>
                            <h3 style={{ margin: 0 }}>Interactive Risk Analysis</h3>
                            <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-muted)' }}>Adjust factors to simulate health outcomes</p>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 300px)', gap: '2rem', alignItems: 'center' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {Object.entries(weights).map(([factor, weight]) => (
                                <div key={factor}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <label style={{ textTransform: 'capitalize', fontSize: '0.875rem', fontWeight: '500' }}>{factor}</label>
                                        <span style={{ fontSize: '0.875rem', fontWeight: '700', color: 'var(--primary)' }}>{weight}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={weight}
                                        onChange={(e) => handleWeightChange(factor, e.target.value)}
                                        style={{ width: '100%' }}
                                    />
                                </div>
                            ))}
                        </div>

                        <div style={{ textAlign: 'center', padding: '1.5rem', backgroundColor: '#f8fafc', borderRadius: '1rem', border: '1px solid #e2e8f0' }}>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>SIMULATED SCORE</div>
                            <div style={{ fontSize: '3rem', fontWeight: '800', color: (simulatedRisk?.risk_score || 0) > 60 ? '#ef4444' : (simulatedRisk?.risk_score || 0) > 30 ? '#f59e0b' : '#10b981' }}>
                                {isSimulating ? '...' : (simulatedRisk?.risk_score || data.risk_score || 0)}
                            </div>
                            <div style={{
                                display: 'inline-block',
                                padding: '0.25rem 0.75rem',
                                borderRadius: '9999px',
                                backgroundColor: (simulatedRisk?.risk_score || 0) > 60 ? '#fee2e2' : (simulatedRisk?.risk_score || 0) > 30 ? '#fef3c7' : '#dcfce7',
                                color: (simulatedRisk?.risk_score || 0) > 60 ? '#991b1b' : (simulatedRisk?.risk_score || 0) > 30 ? '#92400e' : '#166534',
                                fontWeight: '700',
                                fontSize: '0.75rem'
                            }}>
                                {simulatedRisk?.risk_label?.toUpperCase() || data?.risk_label?.toUpperCase() || 'LOW'} RISK
                            </div>
                        </div>
                    </div>
                </div>

                {/* Active Conditions */}
                <div className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3><Thermometer size={20} /> Active Conditions</h3>
                        <button onClick={() => setIsEditingClinical(true)} className="btn-icon-bg" title="Update Conditions">
                            <Edit size={16} />
                        </button>
                    </div>
                    <div className="list-container">
                        {fullConditions.length > 0 ? (
                            fullConditions.map((c, i) => (
                                <div key={i} className="list-item condition-item" style={{ justifyContent: 'space-between' }}>
                                    <span><span className="dot" style={{ backgroundColor: '#ef4444' }}></span> {c.code?.text || "Unknown"}</span>
                                    <button onClick={() => fetchHistory(c.id, 'Condition', c.code?.text)} className="btn-icon" title="View Progress History">
                                        <History size={16} color="var(--text-muted)" />
                                    </button>
                                </div>
                            ))
                        ) : (
                            <p className="empty-state">No active conditions recorded.</p>
                        )}
                    </div>
                </div>

                {/* Medications */}
                <div className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3><Pill size={20} /> Current Medications</h3>
                    </div>
                    <div className="list-container">
                        {medications.length > 0 ? (
                            medications.map((m, i) => (
                                <div key={i} className="list-item medication-item" style={{ justifyContent: 'space-between' }}>
                                    <span>
                                        <span className="dot" style={{ backgroundColor: '#6366f1' }}></span>
                                        {m.medicationCodeableConcept?.text || m.medication?.concept?.text || "Unknown Medication"}
                                    </span>
                                    <button onClick={() => fetchHistory(m.id, 'Medication', m.medicationCodeableConcept?.text || m.medication?.concept?.text)} className="btn-icon" title="View History">
                                        <History size={16} color="var(--text-muted)" />
                                    </button>
                                </div>
                            ))
                        ) : (
                            <p className="empty-state">No active medications.</p>
                        )}
                    </div>
                </div>

                {/* Recommended Plan */}
                <div className="card highlight-card">
                    <div className="card-badge">RECOMMENDED</div>
                    <h3><ShieldCheck size={24} /> Your Best Plan</h3>
                    {recommended_plan ? (
                        <div className="plan-details">
                            <h2 className="plan-name">{recommended_plan.name}</h2>
                            <div className="plan-cost">${recommended_plan.cost}<small>/mo</small></div>
                            <p className="plan-desc">{recommended_plan.description}</p>
                        </div>
                    ) : (
                        <p className="empty-state" style={{ margin: '1rem 0' }}>No specific recommendation found for your profile.</p>
                    )}
                    <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                        <button
                            className={`btn ${activeCoverages.some(c => c.class?.[0]?.value === recommended_plan?.id && c.status === 'active') ? 'btn-success' : 'btn-white'} btn-block`}
                            style={{ flex: 1 }}
                            onClick={() => handleSelectPlan(recommended_plan)}
                            disabled={isSimulating || activeCoverages.some(c => c.class?.[0]?.value === recommended_plan?.id && c.status === 'active')}
                        >
                            {activeCoverages.some(c => c.class?.[0]?.value === recommended_plan?.id && c.status === 'active') ? (
                                <><Check size={18} /> Enrolled</>
                            ) : "Select This Plan"}
                        </button>
                        <Link
                            to="/insurance-plans"
                            state={{ preSelectedPlanId: recommended_plan?.id }}
                            className="btn btn-outline btn-block"
                            style={{ flex: 1, color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                        >
                            Browse More
                        </Link>
                    </div>
                </div>

                {/* Active Insurance Plans */}
                <div className="card full-width">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3><ShieldCheck size={24} /> My Active Insurance Plans</h3>
                        <Link to="/insurance-plans" className="btn btn-outline btn-sm">Add More Plans</Link>
                    </div>

                    <div className="list-container">
                        {activeCoverages.length > 0 ? (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                                {activeCoverages.map((cov, i) => {
                                    const planId = cov.class?.[0]?.value;
                                    const planInfo = data.all_plans?.find(p => p.id === planId) || { name: cov.class?.[0]?.name, cost: '?' };

                                    return (
                                        <div key={cov.id} className="active-plan-item card" style={{ padding: '1.5rem', border: '1px solid #e2e8f0', position: 'relative' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <div>
                                                    <h4 style={{ margin: 0, color: 'var(--primary)' }}>{planInfo.name}</h4>
                                                    <p style={{ margin: '0.25rem 0', fontWeight: 'bold' }}>${planInfo.cost}/mo</p>
                                                </div>
                                                <div className="status-badge" style={{ backgroundColor: '#dcfce7', color: '#166534', fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                                                    ACTIVE
                                                </div>
                                            </div>
                                            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                                <Link to="/insurance-plans" className="btn btn-outline btn-sm" style={{ flex: 1, textAlign: 'center' }}>Change Plan</Link>
                                                <button onClick={() => handleCancelPlan(cov.id)} className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>Cancel</button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="empty-state" style={{ padding: '2rem', textAlign: 'center' }}>
                                <ShieldCheck size={48} color="#cbd5e1" style={{ marginBottom: '1rem' }} />
                                <p>You don't have any active insurance plans.</p>
                                <Link to="/insurance-plans" className="btn btn-primary" style={{ marginTop: '1rem' }}>Browse Plans</Link>
                            </div>
                        )}
                    </div>
                </div>

                {/* Patient Similarity Insights */}
                <div className="card full-width similarity-card">
                    <div className="card-header">
                        <User className="icon" size={24} />
                        <div>
                            <h3>Why this recommendation?</h3>
                            <p className="subtitle">Based on your similarity to {data?.similar_cohort_size || 0} other patients</p>
                        </div>
                    </div>
                    <div className="similarity-content">
                        <div className="similarity-reasons">
                            <h4>Analysis Insights:</h4>
                            <ul>
                                <li><strong>Demographics:</strong> Matched by Gender and Age Group.</li>
                                <li><strong>Clinical Profile:</strong> {fullConditions.length} active conditions analyzed.</li>
                                {data?.similar_patients_preview && data.similar_patients_preview.length > 0 && (
                                    <li><strong>Community Pattern:</strong> Patients like {data.similar_patients_preview[0].split(' ')[0]}... chose this plan.</li>
                                )}
                            </ul>
                        </div>
                        <div className="similarity-summary">
                            <p>We analyzed regional trends and clinical outcomes for patients with shared profiles to ensure this plan offers the best coverage for your specific needs.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card full-width">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3>User Profile</h3>
                    {!isEditingProfile && (
                        <button onClick={() => setIsEditingProfile(true)} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Edit size={16} /> Edit Details
                        </button>
                    )}
                </div>

                {isEditingProfile ? (
                    <form onSubmit={handleUpdateProfile} className="profile-form">
                        <div className="grid-form">
                            <div className="form-group">
                                <label>Full Name</label>
                                <input value={profileForm.name} onChange={e => setProfileForm({ ...profileForm, name: e.target.value })} required />
                            </div>
                            <div className="form-group">
                                <label>Phone Number</label>
                                <input value={profileForm.phone} onChange={e => setProfileForm({ ...profileForm, phone: e.target.value })} />
                            </div>
                            <div className="form-group full-width">
                                <label>Address</label>
                                <input value={profileForm.address} onChange={e => setProfileForm({ ...profileForm, address: e.target.value })} />
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                            <button type="submit" className="btn btn-primary"><Save size={16} /> Save Changes</button>
                            <button type="button" onClick={() => setIsEditingProfile(false)} className="btn btn-outline">Cancel</button>
                        </div>
                    </form>
                ) : (
                    <div className="profile-details" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                        <div className="detail-item">
                            <label>Patient ID</label>
                            <span style={{ fontFamily: 'monospace' }}>{user.patientId}</span>
                        </div>
                        <div className="detail-item">
                            <label>Name</label>
                            <span>{profileForm.name || user?.name || 'N/A'}</span>
                        </div>
                        <div className="detail-item">
                            <label>Phone</label>
                            <span>{profileForm.phone || 'N/A'}</span>
                        </div>
                        <div className="detail-item full-width">
                            <label>Address</label>
                            <span>{profileForm.address || 'N/A'}</span>
                        </div>
                        {!data.patientResource && (
                            <div className="detail-item full-width" style={{ marginTop: '1rem', color: '#ef4444', fontStyle: 'italic' }}>
                                Note: Advanced medical profile not found in database.
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Clinical Update Modal */}
            {isEditingClinical && (
                <div className="modal-overlay">
                    <div className="modal-card">
                        <div className="modal-header">
                            <h3>Update Health Conditions & Vitals</h3>
                            <button onClick={() => setIsEditingClinical(false)} className="btn-icon"><X size={24} /></button>
                        </div>
                        <form onSubmit={handleUpdateClinical} className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div className="form-section">
                                <MultiSelect
                                    label="Active Conditions"
                                    options={regData.conditions || []}
                                    selected={clinicalForm.conditions}
                                    onChange={(selected) => setClinicalForm(prev => ({ ...prev, conditions: selected }))}
                                    placeholder="Search and select conditions..."
                                />
                            </div>

                            <div className="form-section">
                                <MultiSelect
                                    label="Current Medications"
                                    options={regData.medications || []}
                                    selected={clinicalForm.medications}
                                    onChange={(selected) => setClinicalForm(prev => ({ ...prev, medications: selected }))}
                                    placeholder="Search and select medications..."
                                />
                            </div>

                            <div className="form-section">
                                <div className="form-group" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                                    <select
                                        value={selectedObsToAdd}
                                        onChange={(e) => setSelectedObsToAdd(e.target.value)}
                                        style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#f8fafc', height: '48px' }}
                                    >
                                        <option value="">Choose an observation to add...</option>
                                        {regData.observations.map(obs => (
                                            <option key={obs[0]} value={obs[0]}>{obs[0]} ({obs[1]})</option>
                                        ))}
                                    </select>
                                    <button type="button" onClick={addObservation} className="btn btn-primary" style={{ padding: '0 1.5rem', height: '48px' }}>
                                        <PlusCircle size={18} /> Add
                                    </button>
                                </div>

                                <div className="observations-list">
                                    {clinicalForm.vitals?.extras?.map(obs => (
                                        <div key={obs.name} className="observation-row">
                                            <div className="form-group" style={{ margin: 0 }}>
                                                <label className="form-label">{obs.name} ({obs.unit})</label>
                                                <input
                                                    type="number"
                                                    value={obs.value}
                                                    onChange={(e) => handleExtraObsChange(obs.name, e.target.value)}
                                                    placeholder="Enter value"
                                                />
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => removeObservation(obs.name)}
                                                className="btn-icon"
                                                title="Remove"
                                            >
                                                <Trash2 size={20} />
                                            </button>
                                        </div>
                                    ))}
                                    {(!clinicalForm.vitals?.extras || clinicalForm.vitals.extras.length === 0) && (
                                        <p className="empty-state" style={{ textAlign: 'center', padding: '1rem', background: '#f8fafc', borderRadius: '8px' }}>
                                            No extra observations added yet.
                                        </p>
                                    )}
                                </div>
                            </div>

                            <div className="form-section">
                                <label className="form-label" style={{ borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>Current Vitals</label>
                                <div className="form-grid-3">
                                    <div className="form-group">
                                        <label className="form-label">Systolic BP (mmHg)</label>
                                        <input type="number" placeholder="120" value={clinicalForm.vitals.systolic || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, systolic: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Diastolic BP (mmHg)</label>
                                        <input type="number" placeholder="80" value={clinicalForm.vitals.diastolic || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, diastolic: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Heart Rate (bpm)</label>
                                        <input type="number" placeholder="72" value={clinicalForm.vitals.heartRate || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, heartRate: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Weight (kg)</label>
                                        <input type="number" placeholder="70" value={clinicalForm.vitals.weight || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, weight: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Height (cm)</label>
                                        <input type="number" placeholder="175" value={clinicalForm.vitals.height || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, height: e.target.value } })} />
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={() => setIsEditingClinical(false)} className="btn btn-outline">Cancel</button>
                                <button type="submit" className="btn btn-primary" style={{ padding: '0 2rem' }}>
                                    <Save size={18} /> Update Medical Profile
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Clinical Version History Modal */}
            {showVersionHistory && (
                <div className="modal-overlay">
                    <div className="modal-card" style={{ maxWidth: '45rem', width: '90%' }}>
                        <div className="modal-header">
                            <h3>Clinical Version History</h3>
                            <button onClick={() => setShowVersionHistory(false)} className="btn-icon"><X size={24} /></button>
                        </div>
                        <div className="modal-body" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
                            <div className="version-list">
                                {clinicalHistory.map((v, i) => (
                                    <div key={i} className="version-card">
                                        <div className="version-header">
                                            <span className="version-tag">Version {v.versionNum}</span>
                                            <span className="version-date">{new Date(v.timestamp).toLocaleString()}</span>
                                        </div>
                                        <div className="version-details">
                                            <div className="detail-block">
                                                <strong>Conditions:</strong>
                                                <div className="list-inline">
                                                    {v.conditions.map(c => <span key={c} className="mini-tag">{c}</span>)}
                                                </div>
                                            </div>
                                            <div className="detail-block">
                                                <strong>Vitals:</strong>
                                                <span className="vitals-summary">
                                                    BP: {v.vitals.systolic}/{v.vitals.diastolic} | HR: {v.vitals.heartRate} | W: {v.vitals.weight}kg
                                                </span>
                                            </div>
                                            {v.medications && v.medications.length > 0 && (
                                                <div className="detail-block" style={{ marginTop: '0.5rem' }}>
                                                    <strong>Medications:</strong>
                                                    <div className="list-inline">
                                                        {v.medications.map(m => <span key={m} className="mini-tag" style={{ borderLeft: '2px solid #6366f1' }}>{m}</span>)}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Resource History Modal */}
            {historyModal.isOpen && (
                <div className="modal-overlay">
                    <div className="modal-card" style={{ maxWidth: '30rem' }}>
                        <div className="modal-header">
                            <h3><Clock size={20} /> History: {historyModal.title}</h3>
                            <button onClick={() => setHistoryModal({ ...historyModal, isOpen: false })} className="btn-icon"><X size={24} /></button>
                        </div>
                        <div className="modal-body" style={{ maxHeight: '25rem', overflowY: 'auto', padding: '1rem' }}>
                            {historyData.length > 0 ? (
                                <div className="history-timeline">
                                    {historyData.map((h, i) => (
                                        <div key={i} className="history-item" style={{ borderLeft: '2px solid #e2e8f0', paddingLeft: '1.5rem', marginBottom: '1.5rem', position: 'relative' }}>
                                            <div style={{ position: 'absolute', left: '-6px', top: '0', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#6366f1' }}></div>
                                            <div style={{ fontWeight: '600', fontSize: '0.9rem', color: 'var(--primary)' }}>Version {historyData.length - i}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{new Date(h.timestamp).toLocaleString()}</div>
                                            <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                                                {historyModal.type === 'Condition' ? (
                                                    <div>Status: <span style={{ color: h.data.clinicalStatus?.text === 'Active' ? '#059669' : '#6b7280', fontWeight: 'bold' }}>{h.data.clinicalStatus?.text || 'Active'}</span></div>
                                                ) : (
                                                    <div>Notes: {h.data.note?.[0]?.text || 'Prescribed version'}</div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No previous versions found.</p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {showConsent && <ConsentModal onConsentGiven={handleConsent} />}
        </div>
    );
};

export default PatientDashboard;
