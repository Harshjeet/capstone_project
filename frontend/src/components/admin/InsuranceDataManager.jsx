import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, ShieldCheck, FileCheck, AlertTriangle, Users, CreditCard, Activity } from 'lucide-react';

const InsuranceDataManager = () => {
    const [coverage, setCoverage] = useState([]);
    const [consents, setConsents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [activeTab, setActiveTab] = useState('coverage');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [covRes, conRes] = await Promise.all([
                    axios.get('/admin/insurance/coverage'),
                    axios.get('/admin/insurance/consents')
                ]);
                setCoverage(covRes.data);
                setConsents(conRes.data);
            } catch (error) {
                console.error("Error fetching insurance data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getStatusBadgeStyle = (status) => {
        switch (status?.toLowerCase()) {
            case 'active':
                return {
                    backgroundColor: '#dcfce7',
                    color: '#166534',
                    borderColor: '#bbf7d0'
                };
            case 'cancelled':
                return {
                    backgroundColor: '#fee2e2',
                    color: '#991b1b',
                    borderColor: '#fecaca'
                };
            case 'draft':
                return {
                    backgroundColor: '#f3f4f6',
                    color: '#374151',
                    borderColor: '#e5e7eb'
                };
            default:
                return {
                    backgroundColor: '#fef3c7',
                    color: '#92400e',
                    borderColor: '#fde68a'
                };
        }
    };

    const filteredCoverage = coverage.filter(c =>
        c.beneficiary?.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.class?.[0]?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.status?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const filteredConsents = consents.filter(c =>
        c.patient?.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.status?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <div className="dashboard-container">
                <div className="loading">Loading insurance data...</div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text)' }}>Insurance & Compliance</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Monitor patient insurance coverage and signed consents.</p>

            {/* Header & Search */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <ShieldCheck size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text)', margin: '0' }}>
                            Insurance Management
                        </h3>
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            backgroundColor: '#f1f5f9',
                            color: '#64748b'
                        }}>
                            {coverage.length + consents.length} Total Records
                        </span>
                    </div>
                    <div style={{ position: 'relative', width: '16rem' }}>
                        <Search style={{ position: 'absolute', left: '0.75rem', top: '0.75rem', color: '#9ca3af' }} size={18} />
                        <input
                            type="text"
                            placeholder="Search insurance records..."
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

                {/* Tab Navigation */}
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', borderBottom: '1px solid #e2e8f0' }}>
                    <button
                        onClick={() => setActiveTab('coverage')}
                        style={{
                            padding: '0.75rem 1rem',
                            backgroundColor: activeTab === 'coverage' ? '#f8fafc' : 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'coverage' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'coverage' ? 'var(--primary)' : 'var(--text-muted)',
                            fontWeight: activeTab === 'coverage' ? '600' : '400',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <CreditCard size={16} />
                            Active Coverage ({coverage.length})
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab('consents')}
                        style={{
                            padding: '0.75rem 1rem',
                            backgroundColor: activeTab === 'consents' ? '#f8fafc' : 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'consents' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'consents' ? 'var(--primary)' : 'var(--text-muted)',
                            fontWeight: activeTab === 'consents' ? '600' : '400',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <FileCheck size={16} />
                            Patient Consents ({consents.length})
                        </div>
                    </button>
                </div>
            </div>

            {/* Content based on active tab */}
            {activeTab === 'coverage' && (
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
                                }}>Beneficiary</th>
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
                                }}>Insurance Plan</th>
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
                                }}>Status</th>
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
                                }}>Period</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCoverage.map((cov, index) => (
                                <tr key={cov.id || index}>
                                    <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)', padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        {(index + 1).toString().padStart(2, '0')}
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            <Users size={12} />
                                            <span>{cov.beneficiary?.reference || 'Unknown'}</span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <CreditCard size={14} style={{ color: 'var(--primary)' }} />
                                            <span style={{ fontWeight: '500', color: 'var(--text)' }}>
                                                {cov.class?.[0]?.name || "Unknown Plan"}
                                            </span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            fontWeight: '600',
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '9999px',
                                            border: '1px solid',
                                            textTransform: 'capitalize',
                                            ...getStatusBadgeStyle(cov.status)
                                        }}>
                                            {cov.status || 'active'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        {cov.period?.start ? new Date(cov.period.start).toLocaleDateString() : 'N/A'}
                                    </td>
                                </tr>
                            ))}
                            {filteredCoverage.length === 0 && (
                                <tr>
                                    <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                        {searchTerm ? 'No coverage records found matching your search.' : 'No coverage records found.'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {activeTab === 'consents' && (
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
                                }}>Patient</th>
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
                                }}>Consent Type</th>
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
                                }}>Status</th>
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
                                }}>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredConsents.map((consent, index) => (
                                <tr key={consent.id || index}>
                                    <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)', padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        {(index + 1).toString().padStart(2, '0')}
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            <Users size={12} />
                                            <span>{consent.patient?.reference || 'Unknown'}</span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <FileCheck size={14} style={{ color: 'var(--primary)' }} />
                                            <span style={{ fontWeight: '500', color: 'var(--text)' }}>
                                                {consent.category?.[0]?.coding?.[0]?.display || 'General Consent'}
                                            </span>
                                        </div>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            fontWeight: '600',
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '9999px',
                                            border: '1px solid',
                                            textTransform: 'capitalize',
                                            ...getStatusBadgeStyle(consent.status)
                                        }}>
                                            {consent.status || 'active'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        {consent.dateTime ? new Date(consent.dateTime).toLocaleDateString() : 'N/A'}
                                    </td>
                                </tr>
                            ))}
                            {filteredConsents.length === 0 && (
                                <tr>
                                    <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                        {searchTerm ? 'No consent records found matching your search.' : 'No consent records found.'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default InsuranceDataManager;
