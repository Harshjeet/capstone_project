import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Trash2, ShieldCheck, Mail, Key, Eye, Clipboard, X } from 'lucide-react';

const UserManager = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedFhir, setSelectedFhir] = useState(null);
    const [fhirModalOpen, setFhirModalOpen] = useState(false);
    const [fetchingFhir, setFetchingFhir] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalUsers, setTotalUsers] = useState(0);

    useEffect(() => {
        fetchUsers(currentPage, searchTerm);
    }, [currentPage, searchTerm]);

    const fetchUsers = async (page = 1, search = '') => {
        try {
            const res = await axios.get(`/admin/users?page=${page}&limit=15&search=${search}`);
            setUsers(res.data.data);
            setTotalPages(res.data.total_pages);
            setTotalUsers(res.data.total);
        } catch (error) {
            console.error("Error fetching users:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (userId, username) => {
        if (!window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await axios.delete(`/admin/users/${userId}`);
            setUsers(prev => prev.filter(user => user.id !== userId));
        } catch (error) {
            console.error("Error deleting user:", error);
            alert("Failed to delete user. Please try again.");
        }
    };

    const handleViewFhir = async (patientId) => {
        setFetchingFhir(true);
        try {
            const res = await axios.get(`/admin/patients/${patientId}/fhir`);
            setSelectedFhir(res.data);
            setFhirModalOpen(true);
        } catch (error) {
            console.error("Error fetching FHIR data:", error);
            alert("Failed to fetch FHIR data. Please ensure the patient exists and you have admin access.");
        } finally {
            setFetchingFhir(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert("JSON copied to clipboard!");
    };

    const getRoleBadgeStyle = (role) => {
        switch (role?.toLowerCase()) {
            case 'admin':
                return {
                    backgroundColor: '#fee2e2',
                    color: '#991b1b',
                    borderColor: '#fecaca'
                };
            case 'patient':
                return {
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    borderColor: '#bfdbfe'
                };
            default:
                return {
                    backgroundColor: '#f3f4f6',
                    color: '#374151',
                    borderColor: '#e5e7eb'
                };
        }
    };

    // Filtering is now handled by backend pagination
    const filteredUsers = users;

    if (loading) {
        return (
            <div className="dashboard-container">
                <div className="loading">Loading user data...</div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text)' }}>User Management</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Control system access, roles, and permissions.</p>

            {/* Header & Search */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <ShieldCheck size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text)', margin: '0' }}>
                            System Users
                        </h3>
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            backgroundColor: '#f1f5f9',
                            color: '#64748b'
                        }}>
                            {totalUsers} Total
                        </span>
                    </div>
                    <div style={{ position: 'relative', width: '16rem' }}>
                        <Search style={{ position: 'absolute', left: '0.75rem', top: '0.75rem', color: '#9ca3af' }} size={18} />
                        <input
                            type="text"
                            placeholder="Search users..."
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

            {/* Users Table */}
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
                            }}>User</th>
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
                            }}>Contact</th>
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
                            }}>Role</th>
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
                            }}>Patient Info</th>
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
                        {filteredUsers.map((user, index) => (
                            <tr key={user.id}>
                                <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)', padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                    {((currentPage - 1) * 15 + index + 1).toString().padStart(2, '0')}
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
                                            {user.name?.charAt(0).toUpperCase() || user.username?.charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <span style={{ fontWeight: '600', display: 'block', fontSize: '0.875rem', color: 'var(--text)' }}>
                                                {user.name || 'N/A'}
                                            </span>
                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                                @{user.username}
                                            </span>
                                        </div>
                                    </div>
                                </td>
                                <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        <Mail size={12} />
                                        <span>{user.email || 'No email'}</span>
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
                                        ...getRoleBadgeStyle(user.role)
                                    }}>
                                        {user.role || 'unknown'}
                                    </span>
                                </td>
                                <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0' }}>
                                    {user.patientId ? (
                                        <div style={{ fontSize: '0.75rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                                                <Key size={12} />
                                                <span>ID: {user.patientId.slice(-8)}</span>
                                            </div>
                                            <button
                                                onClick={() => handleViewFhir(user.patientId)}
                                                className="btn btn-outline"
                                                style={{
                                                    padding: '0.2rem 0.5rem',
                                                    fontSize: '0.7rem',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    gap: '0.3rem',
                                                    marginTop: '0.5rem',
                                                    height: 'auto'
                                                }}
                                                disabled={fetchingFhir}
                                            >
                                                <Eye size={12} />
                                                {fetchingFhir ? 'Loading...' : 'View FHIR'}
                                            </button>
                                        </div>
                                    ) : (
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No patient data</span>
                                    )}
                                </td>
                                <td style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e2e8f0', textAlign: 'right' }}>
                                    <button
                                        onClick={() => handleDelete(user.id, user.username || user.name)}
                                        className="btn btn-outline"
                                        style={{
                                            padding: '0.375rem 0.75rem',
                                            fontSize: '0.75rem',
                                            color: '#dc2626',
                                            borderColor: '#dc2626'
                                        }}
                                        title="Delete User"
                                        onMouseEnter={(e) => {
                                            e.target.style.backgroundColor = '#fef2f2';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.target.style.backgroundColor = 'transparent';
                                        }}
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {filteredUsers.length === 0 && (
                            <tr>
                                <td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    {searchTerm ? 'No users found matching your search.' : 'No users found in the system.'}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                    <div style={{
                        padding: '1rem',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        gap: '1rem',
                        borderTop: '1px solid #e2e8f0',
                        backgroundColor: '#f8fafc'
                    }}>
                        <button
                            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                            disabled={currentPage === 1}
                            className="btn btn-outline"
                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                        >
                            Previous
                        </button>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Page <span style={{ fontWeight: '600', color: 'var(--text)' }}>{currentPage}</span> of {totalPages}
                        </div>
                        <button
                            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                            disabled={currentPage === totalPages}
                            className="btn btn-outline"
                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                        >
                            Next
                        </button>
                    </div>
                )}
            </div>

            {/* FHIR Modal */}
            {fhirModalOpen && selectedFhir && (
                <div className="modal-overlay" style={{ zIndex: 1000 }}>
                    <div className="modal-content" style={{ maxWidth: '800px', width: '90%' }}>
                        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <ShieldCheck size={24} color="var(--primary)" />
                                <div>
                                    <h3 style={{ margin: 0 }}>FHIR Data Resource</h3>
                                    <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        Raw JSON Bundle for Patient: {selectedFhir.entry?.[0]?.resource?.name?.[0]?.text || 'N/A'}
                                    </p>
                                </div>
                            </div>
                            <button className="btn-icon" onClick={() => setFhirModalOpen(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body" style={{ padding: '1rem' }}>
                            <div style={{
                                backgroundColor: '#1e293b',
                                color: '#f8fafc',
                                padding: '1rem',
                                borderRadius: '8px',
                                overflow: 'auto',
                                maxHeight: '500px',
                                position: 'relative'
                            }}>
                                <button
                                    onClick={() => copyToClipboard(JSON.stringify(selectedFhir, null, 2))}
                                    style={{
                                        position: 'absolute',
                                        top: '0.5rem',
                                        right: '0.5rem',
                                        background: 'rgba(255,255,255,0.1)',
                                        border: 'none',
                                        borderRadius: '4px',
                                        color: 'white',
                                        padding: '0.4rem',
                                        cursor: 'pointer'
                                    }}
                                    title="Copy to Clipboard"
                                >
                                    <Clipboard size={16} />
                                </button>
                                <pre style={{ margin: 0, fontSize: '0.85rem' }}>
                                    {JSON.stringify(selectedFhir, null, 2)}
                                </pre>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setFhirModalOpen(false)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManager;
