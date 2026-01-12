import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Trash2, ShieldCheck, Mail, Key } from 'lucide-react';

const UserManager = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const res = await axios.get('/admin/users');
                setUsers(res.data);
            } catch (error) {
                console.error("Error fetching users:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchUsers();
    }, []);

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

    const filteredUsers = users.filter(user =>
        user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.role?.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
                            {users.length} Total
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
                                    {(index + 1).toString().padStart(2, '0')}
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
                                            {user.insurancePlan && (
                                                <div style={{ color: 'var(--text-muted)' }}>
                                                    Plan: {user.insurancePlan}
                                                </div>
                                            )}
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
            </div>
        </div>
    );
};

export default UserManager;
