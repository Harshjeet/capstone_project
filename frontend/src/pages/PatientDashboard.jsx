import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Activity, Pill, ShieldCheck, Thermometer, User, Edit, History, X, Check, Save, Clock, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import ConsentModal from '../components/ConsentModal';

const PatientDashboard = () => {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [medications, setMedications] = useState([]);
    const [fullConditions, setFullConditions] = useState([]);
    const [showConsent, setShowConsent] = useState(false);
    const [consentGiven, setConsentGiven] = useState(false);

    // Edit Profile State
    const [isEditingProfile, setIsEditingProfile] = useState(false);
    const [profileForm, setProfileForm] = useState({ name: user?.name || '', address: '', phone: '' });

    // History & Version State
    const [historyData, setHistoryData] = useState([]);
    const [historyModal, setHistoryModal] = useState({ isOpen: false, title: '', type: '' });
    const [clinicalHistory, setClinicalHistory] = useState([]);
    const [isEditingClinical, setIsEditingClinical] = useState(false);
    const [clinicalForm, setClinicalForm] = useState({ conditions: [], vitals: {} });
    const [showVersionHistory, setShowVersionHistory] = useState(false);

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
                axios.get(`/Patient/${user.patientId}/clinical-history`)
            ]);

            const [recRes, medRes, riskRes, condRes, patientRes, clinicalHistRes] = results;

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

            if (clinicalHistRes.status === 'fulfilled') {
                const hist = clinicalHistRes.value.data;
                setClinicalHistory(hist);
                if (hist.length > 0) {
                    setClinicalForm({
                        conditions: hist[0].conditions || [],
                        vitals: hist[0].vitals || {}
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
            const current = [...prev.conditions];
            if (current.includes(cond)) {
                return { ...prev, conditions: current.filter(c => c !== cond) };
            } else {
                return { ...prev, conditions: [...current, cond] };
            }
        });
    };

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
                        {data?.risk_label ? (
                            <div className={`risk-badge risk-${data.risk_label.toLowerCase()}`}>
                                Risk Level: {data.risk_label} (Score: {data.risk_score})
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
                                    <span><span className="dot" style={{ backgroundColor: '#6366f1' }}></span> {m.medicationCodeableConcept?.text || "Unknown Medication"}</span>
                                    <button onClick={() => fetchHistory(m.id, 'Medication', m.medicationCodeableConcept?.text)} className="btn-icon" title="View History">
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
                    <Link to="/insurance-plans" className="btn btn-white btn-block">View All Plans & Enroll</Link>
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
                    <div className="modal-card" style={{ maxWidth: '40rem' }}>
                        <div className="modal-header">
                            <h3>Update Health Conditions & Vitals</h3>
                            <button onClick={() => setIsEditingClinical(false)} className="btn-icon"><X size={24} /></button>
                        </div>
                        <form onSubmit={handleUpdateClinical} className="modal-body">
                            <div className="form-section">
                                <h4>Select Active Conditions</h4>
                                <div className="conditions-selection" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
                                    {ALLOWED_CONDITIONS.map(c => (
                                        <button
                                            key={c}
                                            type="button"
                                            className={`tag-btn ${clinicalForm.conditions.includes(c) ? 'active' : ''}`}
                                            onClick={() => toggleCondition(c)}
                                        >
                                            {c}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="form-section">
                                <h4>Current Vitals</h4>
                                <div className="grid-form" style={{ gridTemplateColumns: '1fr 1fr' }}>
                                    <div className="form-group">
                                        <label>Systolic BP (mmHg)</label>
                                        <input type="number" value={clinicalForm.vitals.systolic || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, systolic: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label>Diastolic BP (mmHg)</label>
                                        <input type="number" value={clinicalForm.vitals.diastolic || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, diastolic: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label>Heart Rate (bpm)</label>
                                        <input type="number" value={clinicalForm.vitals.heartRate || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, heartRate: e.target.value } })} />
                                    </div>
                                    <div className="form-group">
                                        <label>Weight (kg)</label>
                                        <input type="number" value={clinicalForm.vitals.weight || ''} onChange={e => setClinicalForm({ ...clinicalForm, vitals: { ...clinicalForm.vitals, weight: e.target.value } })} />
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={() => setIsEditingClinical(false)} className="btn btn-outline">Cancel</button>
                                <button type="submit" className="btn btn-primary">Create New Version</button>
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
