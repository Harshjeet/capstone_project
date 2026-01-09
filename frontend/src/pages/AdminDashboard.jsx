import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import PlanManager from '../components/PlanManager';
import PatientManager from '../components/PatientManager';
import ClinicalDataManager from '../components/admin/ClinicalDataManager';
import InsuranceDataManager from '../components/admin/InsuranceDataManager';
import UserManager from '../components/admin/UserManager';
import AdminAnalytics from '../components/AdminAnalytics';
import { LayoutDashboard, Users, FileText, Activity, LogOut, ShieldCheck, Database, Stethoscope, Briefcase } from 'lucide-react';

const AdminDashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('analytics');
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        if (!user || user.role !== 'admin') {
            navigate('/login');
        }
    }, [user, navigate]);

    useEffect(() => {
        if (activeTab === 'logs') fetchLogs();
    }, [activeTab]);

    const fetchLogs = async () => {
        try {
            const res = await axios.get('/admin/system/logs');
            setLogs(res.data);
        } catch (err) {
            console.error("Failed to fetch logs", err);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user || user.role !== 'admin') return null;

    const SidebarItem = ({ id, label, icon: Icon }) => (
        <button
            onClick={() => setActiveTab(id)}
            className={`nav-btn ${activeTab === id ? 'active' : ''}`}
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: 'none',
                background: activeTab === id ? 'var(--primary)' : 'transparent',
                color: activeTab === id ? 'white' : 'var(--text-muted)',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s',
                textAlign: 'left'
            }}
        >
            <Icon size={18} />
            <span>{label}</span>
        </button>
    );

    return (
        <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--background)' }}>
            {/* Sidebar */}
            <aside style={{
                width: '280px',
                backgroundColor: 'var(--surface)',
                borderRight: '1px solid #e2e8f0',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingBottom: '1rem', borderBottom: '1px solid #e2e8f0' }}>
                    <div style={{
                        backgroundColor: 'var(--primary)',
                        color: 'white',
                        padding: '0.5rem',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <ShieldCheck size={20} />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0', color: 'var(--text)' }}>AdminPortal</h1>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0' }}>Enterprise Suite</p>
                    </div>
                </div>

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div>
                        <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', margin: '0 0 0.5rem 0' }}>Overview</h3>
                        <SidebarItem id="analytics" label="Dashboard & Risks" icon={LayoutDashboard} />
                    </div>

                    <div>
                        <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', margin: '0 0 0.5rem 0' }}>Management</h3>
                        <SidebarItem id="patients" label="Patient Directory" icon={Users} />
                        <SidebarItem id="users" label="User Access" icon={Database} />
                        <SidebarItem id="plans" label="Insurance Plans" icon={FileText} />
                    </div>

                    <div>
                        <h3 style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', margin: '0 0 0.5rem 0' }}>Clinical & Compliance</h3>
                        <SidebarItem id="clinical" label="Clinical Registry" icon={Stethoscope} />
                        <SidebarItem id="insurance" label="Consent & Coverage" icon={Briefcase} />
                        <SidebarItem id="logs" label="System Audit" icon={Activity} />
                    </div>
                </div>

                <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                        <div style={{
                            width: '2rem',
                            height: '2rem',
                            borderRadius: '50%',
                            backgroundColor: 'var(--primary)',
                            color: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.75rem',
                            fontWeight: '700'
                        }}>
                            AD
                        </div>
                        <div>
                            <p style={{ margin: '0', fontSize: '0.875rem', fontWeight: '500', color: 'var(--text)' }}>System Admin</p>
                            <p style={{ margin: '0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>admin@hospital.com</p>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
                        <LogOut size={14} /> Log Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <header style={{
                    backgroundColor: 'var(--surface)',
                    borderBottom: '1px solid #e2e8f0',
                    padding: '1rem 2rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div>
                        <h2 style={{
                            fontSize: '1.5rem',
                            fontWeight: '700',
                            margin: '0 0 0.25rem 0',
                            color: 'var(--text)'
                        }}>
                            {activeTab === 'plans' && 'Insurance Configuration'}
                            {activeTab === 'patients' && 'Patient Directory'}
                            {activeTab === 'users' && 'User Management'}
                            {activeTab === 'clinical' && 'Clinical Data Registry'}
                            {activeTab === 'insurance' && 'Insurance & Consents'}
                            {activeTab === 'analytics' && 'Dashboard Overview'}
                            {activeTab === 'logs' && 'System Audit Logs'}
                        </h2>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', margin: '0' }}>
                            {activeTab === 'plans' ? 'Configure insurance plans, coverage limits, and pricing structures.' :
                                activeTab === 'patients' ? 'Manage patient records and view clinical history.' :
                                    activeTab === 'users' ? 'Control system access, roles, and permissions.' :
                                        activeTab === 'clinical' ? 'Centralized view of medical conditions and observations.' :
                                            activeTab === 'insurance' ? 'Monitor patient insurance coverage and signed consents.' :
                                                activeTab === 'analytics' ? 'High-level insights into population health and system performance.' :
                                                    'Track security events, errors, and system activities.'}
                        </p>
                    </div>
                    <div>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.25rem 0.75rem',
                            backgroundColor: '#dcfce7',
                            color: '#166534',
                            border: '1px solid #bbf7d0',
                            borderRadius: '9999px',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                        }}>
                            <span style={{
                                display: 'inline-block',
                                width: '8px',
                                height: '8px',
                                backgroundColor: '#22c55e',
                                borderRadius: '50%',
                                animation: 'pulse 2s infinite'
                            }}></span>
                            System Operational
                        </div>
                    </div>
                </header>

                <div className="dashboard-container">
                    {activeTab === 'analytics' && <AdminAnalytics />}
                    {activeTab === 'plans' && <PlanManager />}
                    {activeTab === 'patients' && <PatientManager />}
                    {activeTab === 'users' && <UserManager />}
                    {activeTab === 'clinical' && <ClinicalDataManager />}
                    {activeTab === 'insurance' && <InsuranceDataManager />}

                    {activeTab === 'logs' && (
                        <div className="card">
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Activity size={16} style={{ color: 'var(--primary)' }} /> Live Audit Stream
                            </h3>
                            <button onClick={fetchLogs} className="btn btn-outline" style={{ fontSize: '0.75rem', marginTop: '1rem' }}>Refresh</button>
                            <div style={{ maxHeight: '600px', overflowY: 'auto', marginTop: '1rem' }}>
                                {logs.map((log, i) => (
                                    <div key={i} style={{
                                        display: 'flex',
                                        gap: '1rem',
                                        padding: '0.75rem',
                                        borderBottom: '1px solid #e2e8f0',
                                        fontFamily: 'monospace',
                                        fontSize: '0.875rem'
                                    }}>
                                        <span style={{ color: 'var(--text-muted)', width: '140px', flexShrink: 0, fontSize: '0.75rem' }}>
                                            {log.timestamp}
                                        </span>
                                        <span style={{
                                            fontWeight: '700',
                                            width: '60px',
                                            fontSize: '0.75rem',
                                            color: log.level === 'INFO' ? '#22c55e' : log.level === 'WARN' ? '#eab308' : '#ef4444'
                                        }}>
                                            {log.level}
                                        </span>
                                        <span>{log.message}</span>
                                    </div>
                                ))}
                                {logs.length === 0 && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No logs available.</div>}
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;
