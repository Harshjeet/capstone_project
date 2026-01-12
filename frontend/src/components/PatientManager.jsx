import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Eye, FileJson, X, Search, Activity, User, Trash2, AlertTriangle, ShieldCheck, Calendar, MapPin } from 'lucide-react';

const PatientManager = () => {
    const [patients, setPatients] = useState([]);
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [fhirData, setFhirData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [viewMode, setViewMode] = useState('table'); // 'table' or 'grid'
    const [patientDetails, setPatientDetails] = useState({});

    useEffect(() => {
        fetchPatients();
    }, []);

    const fetchPatients = async () => {
        try {
            const res = await axios.get('/admin/patients');
            setPatients(res.data);
            // Fetch additional details for each patient
            res.data.forEach(patient => {
                fetchPatientDetails(patient.id);
            });
        } catch (err) {
            console.error("Failed to fetch patients", err);
        }
    };

    const fetchPatientDetails = async (patientId) => {
        try {
            const [fhirRes, riskRes] = await Promise.all([
                axios.get(`/admin/patients/${patientId}/fhir`),
                axios.get(`/Patient/${patientId}/risk`)
            ]);

            const bundle = fhirRes.data;
            const conditions = bundle.entry?.filter(e => e.resource.resourceType === 'Condition') || [];
            const observations = bundle.entry?.filter(e => e.resource.resourceType === 'Observation') || [];
            const medications = bundle.entry?.filter(e => e.resource.resourceType === 'MedicationRequest') || [];

            setPatientDetails(prev => ({
                ...prev,
                [patientId]: {
                    conditions: conditions.length,
                    observations: observations.length,
                    medications: medications.length,
                    riskScore: riskRes.data.risk_score || 0,
                    riskLabel: riskRes.data.risk_label || 'Unknown'
                }
            }));
        } catch (err) {
            console.error(`Failed to fetch details for patient ${patientId}`, err);
        }
    };

    const handleViewFhir = async (patient) => {
        setSelectedPatient(patient);
        setLoading(true);
        try {
            const res = await axios.get(`/admin/patients/${patient.id}/fhir`);
            setFhirData(res.data);
        } catch (err) {
            console.error("Failed to fetch FHIR data", err);
            setFhirData({ error: "Failed to load FHIR Bundle" });
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (patientId) => {
        if (!window.confirm("Are you sure you want to delete this patient? This cannot be undone.")) return;
        try {
            await axios.delete(`/admin/patients/${patientId}`);
            setPatients(prev => prev.filter(p => p.id !== patientId));
        } catch (err) {
            alert("Failed to delete patient");
        }
    };

    const closeViewer = () => {
        setSelectedPatient(null);
        setFhirData(null);
    };

    const calculateAge = (birthDate) => {
        if (!birthDate) return 'Unknown';
        const birth = new Date(birthDate);
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        return age;
    };

    const getRiskColor = (label) => {
        switch (label?.toLowerCase()) {
            case 'low': return 'bg-green-50 text-green-700 border-green-100';
            case 'medium': return 'bg-yellow-50 text-yellow-700 border-yellow-100';
            case 'high': return 'bg-red-50 text-red-700 border-red-100';
            default: return 'bg-gray-50 text-gray-700 border-gray-100';
        }
    };



    const filteredPatients = patients.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="dashboard-container">
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text)' }}>Patient Directory</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Manage patient records and view clinical history.</p>

            {/* Header & Search */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <User size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text)', margin: '0' }}>
                            Patient Directory
                        </h3>
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            backgroundColor: '#f1f5f9',
                            color: '#64748b'
                        }}>
                            {patients.length} Total
                        </span>
                    </div>
                    <div style={{ position: 'relative', width: '16rem' }}>
                        <Search style={{ position: 'absolute', left: '0.75rem', top: '0.75rem', color: '#9ca3af' }} size={18} />
                        <input
                            type="text"
                            placeholder="Search..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            style={{
                                width: '100%',
                                paddingLeft: '2.5rem',
                                paddingRight: '1rem',
                                padding: '0.5rem',
                                border: '1px solid #e2e8f0',
                                borderRadius: '8px',
                                backgroundColor: '#f8fafc',
                                color: 'var(--text)',
                                fontSize: '0.875rem'
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Patient Table */}
            <div className="card">
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                        <tr>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>#</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>Patient Name</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>ID / Gender</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>Age / Location</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>Clinical Data</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'left'
                            }}>Risk Assessment</th>
                            <th style={{
                                backgroundColor: '#f8fafc',
                                color: 'var(--text-muted)',
                                fontWeight: '500',
                                padding: '0.75rem 1rem',
                                borderBottom: '1px solid #e2e8f0',
                                textTransform: 'uppercase',
                                fontSize: '0.75rem',
                                letterSpacing: '0.05em',
                                textAlign: 'right'
                            }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredPatients.map(p => {
                            const details = patientDetails[p.id] || {};
                            return (
                                <tr key={p.id}>
                                    <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)', padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        {(filteredPatients.indexOf(p) + 1).toString().padStart(2, '0')}
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            <div style={{
                                                width: '2.5rem',
                                                height: '2.5rem',
                                                borderRadius: '50%',
                                                backgroundColor: '#dbeafe',
                                                color: '#1e40af',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontWeight: '700',
                                                fontSize: '0.875rem'
                                            }}>
                                                {p.name.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                <span style={{ fontWeight: '600', display: 'block', fontSize: '0.875rem', color: 'var(--text)' }}>{p.name}</span>
                                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Patient</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', marginBottom: '0.25rem', color: 'var(--text-muted)' }}>ID: {p.id.slice(-6)}</div>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            fontWeight: '500',
                                            padding: '0.125rem 0.5rem',
                                            borderRadius: '4px',
                                            backgroundColor: '#f1f5f9',
                                            color: 'var(--text)',
                                            textTransform: 'capitalize'
                                        }}>{p.gender}</span>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            <Calendar size={12} />
                                            <span>{calculateAge(p.birthDate)} years</span>
                                        </div>
                                        {p.address && (
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', marginTop: '0.25rem', color: 'var(--text-muted)' }}>
                                                <MapPin size={12} />
                                                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '5rem' }}>{p.address}</span>
                                            </div>
                                        )}
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.75rem', flexWrap: 'wrap' }}>
                                            <span style={{
                                                padding: '0.25rem 0.625rem',
                                                backgroundColor: '#dbeafe',
                                                color: '#1e40af',
                                                borderRadius: '6px',
                                                fontWeight: '500',
                                                border: '1px solid #bfdbfe'
                                            }}>
                                                {details.conditions || 0} Conds
                                            </span>
                                            <span style={{
                                                padding: '0.25rem 0.625rem',
                                                backgroundColor: '#dcfce7',
                                                color: '#166534',
                                                borderRadius: '6px',
                                                fontWeight: '500',
                                                border: '1px solid #bbf7d0'
                                            }}>
                                                {details.observations || 0} Obs
                                            </span>
                                            <span style={{
                                                padding: '0.25rem 0.625rem',
                                                backgroundColor: '#f3e8ff',
                                                color: '#6b21a8',
                                                borderRadius: '6px',
                                                fontWeight: '500',
                                                border: '1px solid #e9d5ff'
                                            }}>
                                                {details.medications || 0} Meds
                                            </span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                <ShieldCheck size={14} style={{ color: '#9ca3af' }} />
                                                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#6b7280' }}>{details.riskScore || 0}</span>
                                            </div>
                                            <span style={{
                                                fontSize: '0.75rem',
                                                fontWeight: '700',
                                                padding: '0.25rem 0.5rem',
                                                borderRadius: '9999px',
                                                border: '1px solid',
                                                ...(details.riskLabel?.toLowerCase() === 'low' && {
                                                    backgroundColor: '#dcfce7',
                                                    color: '#166534',
                                                    borderColor: '#bbf7d0'
                                                }),
                                                ...(details.riskLabel?.toLowerCase() === 'medium' && {
                                                    backgroundColor: '#fef3c7',
                                                    color: '#92400e',
                                                    borderColor: '#fde68a'
                                                }),
                                                ...(details.riskLabel?.toLowerCase() === 'high' && {
                                                    backgroundColor: '#fee2e2',
                                                    color: '#991b1b',
                                                    borderColor: '#fecaca'
                                                }),
                                                ...(!details.riskLabel && {
                                                    backgroundColor: '#f3f4f6',
                                                    color: '#374151',
                                                    borderColor: '#e5e7eb'
                                                })
                                            }}>
                                                {details.riskLabel || 'Unknown'}
                                            </span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0', textAlign: 'right' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                                            <button
                                                onClick={() => handleViewFhir(p)}
                                                className="btn btn-outline"
                                                style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}
                                                title="View Clinical Profile"
                                            >
                                                <FileJson size={18} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(p.id)}
                                                className="btn btn-outline"
                                                style={{
                                                    padding: '0.375rem 0.75rem',
                                                    fontSize: '0.75rem',
                                                    color: '#dc2626',
                                                    borderColor: '#dc2626'
                                                }}
                                                title="Delete Patient Record"
                                                onMouseEnter={(e) => {
                                                    e.target.style.backgroundColor = '#fef2f2';
                                                }}
                                                onMouseLeave={(e) => {
                                                    e.target.style.backgroundColor = 'transparent';
                                                }}
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                        {filteredPatients.length === 0 && (
                            <tr>
                                <td colSpan="7" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    No patients found matching your search.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Enhanced FHIR Viewer Modal */}
            {selectedPatient && (
                <div style={{
                    position: 'fixed',
                    inset: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 50,
                    padding: '1rem'
                }}>
                    <div style={{
                        backgroundColor: 'var(--surface)',
                        borderRadius: '1rem',
                        width: '100%',
                        maxWidth: '72rem',
                        height: '90vh',
                        display: 'flex',
                        flexDirection: 'column',
                        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            padding: '1.25rem',
                            borderBottom: '1px solid #e2e8f0',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            backgroundColor: '#f8fafc'
                        }}>
                            <div>
                                <h3 style={{
                                    fontWeight: '700',
                                    fontSize: '1.25rem',
                                    color: '#1f2937',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    margin: '0'
                                }}>
                                    <Activity style={{ color: 'var(--primary)' }} />
                                    Clinical Profile: {selectedPatient.name}
                                </h3>
                                <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0.25rem 0 0 0' }}>
                                    Comprehensive Patient Health Record
                                </p>
                            </div>
                            <button
                                onClick={closeViewer}
                                style={{
                                    padding: '0.5rem',
                                    backgroundColor: 'transparent',
                                    border: 'none',
                                    borderRadius: '9999px',
                                    cursor: 'pointer',
                                    transition: 'background-color 0.2s'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.backgroundColor = '#e5e7eb';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.backgroundColor = 'transparent';
                                }}
                            >
                                <X size={24} style={{ color: '#6b7280' }} />
                            </button>
                        </div>

                        <div style={{ flex: 1, overflow: 'hidden' }}>
                            {loading ? (
                                <div style={{
                                    height: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '0.5rem'
                                }}>
                                    <div style={{
                                        width: '1rem',
                                        height: '1rem',
                                        backgroundColor: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'bounce 1s infinite'
                                    }}></div>
                                    <div style={{
                                        width: '1rem',
                                        height: '1rem',
                                        backgroundColor: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'bounce 1s infinite 0.1s'
                                    }}></div>
                                    <div style={{
                                        width: '1rem',
                                        height: '1rem',
                                        backgroundColor: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'bounce 1s infinite 0.2s'
                                    }}></div>
                                </div>
                            ) : fhirData ? (
                                <div style={{ height: '100%', overflow: 'auto' }}>
                                    {/* Summary Cards */}
                                    <div style={{
                                        padding: '1.5rem',
                                        backgroundColor: '#f8fafc',
                                        borderBottom: '1px solid #e2e8f0'
                                    }}>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                                            <div className="card" style={{ padding: '1rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', marginBottom: '0.5rem' }}>
                                                    <FileJson size={16} />
                                                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Conditions</span>
                                                </div>
                                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1f2937' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'Condition').length || 0}
                                                </div>
                                            </div>
                                            <div className="card" style={{ padding: '1rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#059669', marginBottom: '0.5rem' }}>
                                                    <Activity size={16} />
                                                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Observations</span>
                                                </div>
                                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1f2937' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'Observation').length || 0}
                                                </div>
                                            </div>
                                            <div className="card" style={{ padding: '1rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#7c3aed', marginBottom: '0.5rem' }}>
                                                    <ShieldCheck size={16} />
                                                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Medications</span>
                                                </div>
                                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1f2937' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'MedicationRequest').length || 0}
                                                </div>
                                            </div>
                                            <div className="card" style={{ padding: '1rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ea580c', marginBottom: '0.5rem' }}>
                                                    <AlertTriangle size={16} />
                                                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Risk Score</span>
                                                </div>
                                                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1f2937' }}>
                                                    {patientDetails[selectedPatient.id]?.riskScore || 'N/A'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Detailed Data */}
                                    <div style={{ padding: '1.5rem' }}>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                                            {/* Conditions */}
                                            <div className="card">
                                                <div style={{
                                                    padding: '1rem',
                                                    borderBottom: '1px solid #e2e8f0',
                                                    backgroundColor: '#f8fafc'
                                                }}>
                                                    <h4 style={{ fontWeight: '600', color: '#1f2937', margin: '0' }}>Medical Conditions</h4>
                                                </div>
                                                <div style={{ padding: '1rem', maxHeight: '16rem', overflowY: 'auto' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'Condition').map((entry, idx) => (
                                                        <div key={idx} style={{
                                                            marginBottom: '0.75rem',
                                                            padding: '0.75rem',
                                                            backgroundColor: '#fef2f2',
                                                            borderRadius: '8px',
                                                            border: '1px solid #fecaca'
                                                        }}>
                                                            <div style={{ fontWeight: '500', color: '#991b1b' }}>
                                                                {entry.resource.code?.text || 'Unknown Condition'}
                                                            </div>
                                                            <div style={{ fontSize: '0.75rem', color: '#dc2626', marginTop: '0.25rem' }}>
                                                                Status: {entry.resource.clinicalStatus?.text || 'Active'}
                                                            </div>
                                                        </div>
                                                    )) || <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>No conditions recorded</div>}
                                                </div>
                                            </div>

                                            {/* Observations */}
                                            <div className="card">
                                                <div style={{
                                                    padding: '1rem',
                                                    borderBottom: '1px solid #e2e8f0',
                                                    backgroundColor: '#f8fafc'
                                                }}>
                                                    <h4 style={{ fontWeight: '600', color: '#1f2937', margin: '0' }}>Clinical Observations</h4>
                                                </div>
                                                <div style={{ padding: '1rem', maxHeight: '16rem', overflowY: 'auto' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'Observation').map((entry, idx) => (
                                                        <div key={idx} style={{
                                                            marginBottom: '0.75rem',
                                                            padding: '0.75rem',
                                                            backgroundColor: '#f0fdf4',
                                                            borderRadius: '8px',
                                                            border: '1px solid #bbf7d0'
                                                        }}>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                                <div style={{ fontWeight: '500', color: '#166534' }}>
                                                                    {entry.resource.code?.text || 'Unknown Observation'}
                                                                </div>
                                                                <div style={{ fontWeight: '700', color: '#166534', fontSize: '1rem' }}>
                                                                    {entry.resource.valueQuantity ?
                                                                        `${entry.resource.valueQuantity.value} ${entry.resource.valueQuantity.unit || ''}` :
                                                                        entry.resource.valueString || 'N/A'}
                                                                </div>
                                                            </div>
                                                            <div style={{ fontSize: '0.75rem', color: '#15803d', marginTop: '0.25rem' }}>
                                                                Status: {entry.resource.status || 'Final'}
                                                            </div>
                                                        </div>
                                                    )) || <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>No observations recorded</div>}
                                                </div>
                                            </div>

                                            {/* Medications */}
                                            <div className="card">
                                                <div style={{
                                                    padding: '1rem',
                                                    borderBottom: '1px solid #e2e8f0',
                                                    backgroundColor: '#f8fafc'
                                                }}>
                                                    <h4 style={{ fontWeight: '600', color: '#1f2937', margin: '0' }}>Medications</h4>
                                                </div>
                                                <div style={{ padding: '1rem', maxHeight: '16rem', overflowY: 'auto' }}>
                                                    {fhirData.entry?.filter(e => e.resource.resourceType === 'MedicationRequest').map((entry, idx) => (
                                                        <div key={idx} style={{
                                                            marginBottom: '0.75rem',
                                                            padding: '0.75rem',
                                                            backgroundColor: '#faf5ff',
                                                            borderRadius: '8px',
                                                            border: '1px solid #e9d5ff'
                                                        }}>
                                                            <div style={{ fontWeight: '500', color: '#6b21a8' }}>
                                                                {entry.resource.medicationCodeableConcept?.text || 'Unknown Medication'}
                                                            </div>
                                                            <div style={{ fontSize: '0.75rem', color: '#6b21a8', marginTop: '0.25rem' }}>
                                                                {entry.resource.dosageInstruction?.[0]?.text || 'Standard dosage'}
                                                            </div>
                                                        </div>
                                                    )) || <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>No medications recorded</div>}
                                                </div>
                                            </div>

                                            {/* Raw JSON */}
                                            <div className="card">
                                                <div style={{
                                                    padding: '1rem',
                                                    borderBottom: '1px solid #e2e8f0',
                                                    backgroundColor: '#f8fafc'
                                                }}>
                                                    <h4 style={{ fontWeight: '600', color: '#1f2937', margin: '0' }}>Raw FHIR Data</h4>
                                                </div>
                                                <div style={{
                                                    padding: '1rem',
                                                    maxHeight: '16rem',
                                                    overflowY: 'auto',
                                                    backgroundColor: '#111827',
                                                    color: '#d1d5db',
                                                    fontFamily: 'monospace',
                                                    fontSize: '0.75rem'
                                                }}>
                                                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0 }}>
                                                        {JSON.stringify(fhirData, null, 2)}
                                                    </pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div style={{
                                    height: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#6b7280'
                                }}>
                                    Failed to load patient data
                                </div>
                            )}
                        </div>

                        <div style={{
                            padding: '1rem',
                            borderTop: '1px solid #e2e8f0',
                            backgroundColor: '#f8fafc',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            fontSize: '0.75rem',
                            color: '#6b7280'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <AlertTriangle size={14} style={{ color: '#ea580c' }} />
                                <span>Confidential Patient Data - Handle with Care</span>
                            </div>
                            <span>Standard FHIR R4 Format</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PatientManager;
