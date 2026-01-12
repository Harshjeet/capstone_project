import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Edit2, Trash2, Plus, DollarSign, Shield, X, Check, Users, UserCheck, ShieldCheck } from 'lucide-react';

const PlanManager = () => {
    const [plans, setPlans] = useState([]);
    const [editingPlan, setEditingPlan] = useState(null);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [planSubscriptions, setPlanSubscriptions] = useState({});
    const [formData, setFormData] = useState({
        id: '',
        name: '',
        cost: 0,
        description: '',
        coverage: ''
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchPlans();
    }, []);

    useEffect(() => {
        if (plans.length > 0) {
            fetchPlanSubscriptions();
        }
    }, [plans]);

    const fetchPlans = async () => {
        setLoading(true);
        try {
            console.log("Fetching plans...");
            const res = await axios.get('/admin/plans');
            console.log("Plans fetched:", res.data);
            setPlans(Array.isArray(res.data) ? res.data : []);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch plans:", err);
            setError("Failed to load insurance plans. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const fetchPlanSubscriptions = async () => {
        try {
            // Get all users to see their plan assignments
            const usersRes = await axios.get('/admin/users');
            const subscriptions = {};

            usersRes.data.forEach(user => {
                if (user.insurancePlan) {
                    if (!subscriptions[user.insurancePlan]) {
                        subscriptions[user.insurancePlan] = [];
                    }
                    subscriptions[user.insurancePlan].push({
                        id: user._id,
                        name: user.name,
                        username: user.username,
                        role: user.role
                    });
                }
            });

            setPlanSubscriptions(subscriptions);
        } catch (err) {
            console.error("Failed to fetch plan subscriptions:", err);
            // If endpoint doesn't exist, we'll show empty subscriptions
        }
    };

    const handleEdit = (plan) => {
        setEditingPlan(plan);
        setFormData({
            id: plan.id,
            name: plan.name,
            cost: plan.cost,
            description: plan.description,
            coverage: Array.isArray(plan.coverage) ? plan.coverage.join(', ') : plan.coverage
        });
        setIsFormOpen(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this plan?")) return;
        try {
            await axios.delete(`/admin/plans/${id}`);
            fetchPlans();
        } catch (err) {
            alert("Failed to delete plan");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const payload = {
            ...formData,
            cost: Number(formData.cost),
            coverage: formData.coverage.split(',').map(s => s.trim())
        };

        try {
            if (editingPlan) {
                await axios.put(`/admin/plans/${editingPlan.id}`, payload);
            } else {
                await axios.post('/admin/plans', payload);
            }
            setIsFormOpen(false);
            setEditingPlan(null);
            setFormData({ id: '', name: '', cost: 0, description: '', coverage: '' });
            fetchPlans();
        } catch (err) {
            alert("Failed to save plan");
        }
    };

    return (
        <div className="dashboard-container">
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text)' }}>Insurance Configuration</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Configure insurance plans, coverage limits, and pricing structures.</p>

            {/* Header & Create Button */}
            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <ShieldCheck size={20} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text)', margin: '0' }}>
                            Insurance Plans
                        </h3>
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            backgroundColor: '#f1f5f9',
                            color: '#64748b'
                        }}>
                            {plans.length} Total Plans
                        </span>
                    </div>
                    <button
                        onClick={() => { setIsFormOpen(true); setEditingPlan(null); setFormData({ id: '', name: '', cost: 0, description: '', coverage: '' }); }}
                        className="btn btn-primary"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                        <Plus size={18} /> Create New Plan
                    </button>
                </div>
            </div>

            {/* Loading & Error States */}
            {loading && (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    Loading plans...
                </div>
            )}

            {error && (
                <div style={{
                    padding: '1rem',
                    borderRadius: '8px',
                    backgroundColor: '#fee2e2',
                    color: '#991b1b',
                    marginBottom: '1rem',
                    border: '1px solid #fecaca'
                }}>
                    {error}
                </div>
            )}

            {/* Form Modal */}
            {isFormOpen && (
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
                        maxWidth: '32rem',
                        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            padding: '1.5rem',
                            borderBottom: '1px solid #e2e8f0',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            backgroundColor: '#f8fafc'
                        }}>
                            <h3 style={{
                                fontWeight: '700',
                                fontSize: '1.25rem',
                                color: '#1f2937',
                                margin: '0'
                            }}>
                                {editingPlan ? 'Edit Plan' : 'Create New Plan'}
                            </h3>
                            <button
                                onClick={() => setIsFormOpen(false)}
                                style={{
                                    padding: '0.5rem',
                                    backgroundColor: 'transparent',
                                    border: 'none',
                                    borderRadius: '9999px',
                                    cursor: 'pointer',
                                    transition: 'background-color 0.2s',
                                    color: '#6b7280'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.backgroundColor = '#e5e7eb';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.backgroundColor = 'transparent';
                                }}
                            >
                                <X size={24} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {!editingPlan && (
                                <div>
                                    <label style={{
                                        display: 'block',
                                        fontSize: '0.75rem',
                                        fontWeight: '600',
                                        textTransform: 'uppercase',
                                        marginBottom: '0.5rem',
                                        color: 'var(--text-muted)'
                                    }}>Plan ID (Unique)</label>
                                    <input
                                        style={{
                                            width: '100%',
                                            padding: '0.75rem',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '8px',
                                            backgroundColor: '#f8fafc',
                                            color: 'var(--text)',
                                            fontSize: '0.875rem',
                                            outline: 'none',
                                            transition: 'all 0.2s'
                                        }}
                                        value={formData.id}
                                        onChange={e => setFormData({ ...formData, id: e.target.value })}
                                        placeholder="e.g., gold-premium"
                                        required
                                    />
                                </div>
                            )}
                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.5rem',
                                    color: 'var(--text-muted)'
                                }}>Plan Name</label>
                                <input
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        backgroundColor: '#f8fafc',
                                        color: 'var(--text)',
                                        fontSize: '0.875rem',
                                        outline: 'none',
                                        transition: 'all 0.2s'
                                    }}
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g., Gold Premium"
                                    required
                                />
                            </div>
                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.5rem',
                                    color: 'var(--text-muted)'
                                }}>Monthly Cost ($)</label>
                                <div style={{ position: 'relative' }}>
                                    <span style={{
                                        position: 'absolute',
                                        left: '0.75rem',
                                        top: '0.75rem',
                                        color: 'var(--text-muted)'
                                    }}>$</span>
                                    <input
                                        type="number"
                                        style={{
                                            width: '100%',
                                            padding: '0.75rem',
                                            paddingLeft: '2rem',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '8px',
                                            backgroundColor: '#f8fafc',
                                            color: 'var(--text)',
                                            fontSize: '0.875rem',
                                            outline: 'none',
                                            transition: 'all 0.2s'
                                        }}
                                        value={formData.cost}
                                        onChange={e => setFormData({ ...formData, cost: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.5rem',
                                    color: 'var(--text-muted)'
                                }}>Description</label>
                                <textarea
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        backgroundColor: '#f8fafc',
                                        color: 'var(--text)',
                                        fontSize: '0.875rem',
                                        outline: 'none',
                                        transition: 'all 0.2s',
                                        resize: 'vertical',
                                        minHeight: '4rem'
                                    }}
                                    value={formData.description}
                                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                                    rows="3"
                                />
                            </div>
                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.5rem',
                                    color: 'var(--text-muted)'
                                }}>Coverage (Comma Separated)</label>
                                <input
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        backgroundColor: '#f8fafc',
                                        color: 'var(--text)',
                                        fontSize: '0.875rem',
                                        outline: 'none',
                                        transition: 'all 0.2s'
                                    }}
                                    value={formData.coverage}
                                    onChange={e => setFormData({ ...formData, coverage: e.target.value })}
                                    placeholder="Flu, Fever, Diabetes, etc."
                                />
                            </div>

                            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    style={{ flex: 1 }}
                                >
                                    {editingPlan ? 'Save Changes' : 'Create Plan'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setIsFormOpen(false)}
                                    className="btn btn-outline"
                                    style={{ flex: 1 }}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Plans Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                {plans.length === 0 && !loading && !error && (
                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', backgroundColor: '#f8fafc', borderRadius: '1rem' }}>
                        <p style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>No Insurance Plans Found</p>
                        <p>Create a new plan to get started.</p>
                    </div>
                )}
                {plans.map(plan => {
                    const subscribers = planSubscriptions[plan.id] || [];
                    return (
                        <div key={plan.id} className="card" style={{ position: 'relative' }}>
                            <div style={{
                                position: 'absolute',
                                top: '1rem',
                                right: '1rem',
                                display: 'flex',
                                gap: '0.5rem',
                                transition: 'all 0.2s',
                                zIndex: 10
                            }}>
                                <button
                                    onClick={() => handleEdit(plan)}
                                    className="btn btn-outline"
                                    style={{ padding: '0.5rem', backgroundColor: 'white' }}
                                    title="Edit Plan"
                                >
                                    <Edit2 size={16} />
                                </button>
                                <button
                                    onClick={() => handleDelete(plan.id || plan._id)}
                                    className="btn btn-outline"
                                    style={{
                                        padding: '0.5rem',
                                        color: '#dc2626',
                                        borderColor: '#dc2626',
                                        backgroundColor: 'white'
                                    }}
                                    title="Delete Plan"
                                    onMouseEnter={(e) => {
                                        e.target.style.backgroundColor = '#fef2f2';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.target.style.backgroundColor = 'white';
                                    }}
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>

                            <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{
                                    fontSize: '1.5rem',
                                    fontWeight: '800',
                                    color: 'var(--text)',
                                    margin: '0 0 0.5rem 0'
                                }}>
                                    {plan.name}
                                </h4>
                                <div style={{ display: 'flex', alignItems: 'center', marginTop: '0.25rem', fontWeight: '600', color: '#059669' }}>
                                    <DollarSign size={20} />
                                    <span style={{ fontSize: '1.25rem' }}>{plan.cost}</span>
                                    <span style={{ fontSize: '0.875rem', fontWeight: '400', marginLeft: '0.25rem', color: 'var(--text-muted)' }}>/ mo</span>
                                </div>
                            </div>

                            <p style={{
                                fontSize: '0.875rem',
                                color: 'var(--text-muted)',
                                marginBottom: '1rem',
                                lineHeight: '1.5',
                                height: '3rem',
                                overflow: 'hidden'
                            }}>
                                {plan.description}
                            </p>

                            <div style={{
                                borderTop: '1px solid #e2e8f0',
                                paddingTop: '1rem',
                                marginBottom: '1rem'
                            }}>
                                <p style={{
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.75rem',
                                    color: 'var(--text-muted)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem'
                                }}>
                                    <Shield size={12} /> Coverage Includes
                                </p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                    {(Array.isArray(plan.coverage) ? plan.coverage : String(plan.coverage || '').split(',')).slice(0, 4).map((c, i) => (
                                        <span key={i} style={{
                                            fontSize: '0.75rem',
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '6px',
                                            fontWeight: '500',
                                            border: '1px solid #e2e8f0',
                                            backgroundColor: '#f8fafc',
                                            color: 'var(--text)'
                                        }}>
                                            {c}
                                        </span>
                                    ))}
                                    {(Array.isArray(plan.coverage) ? plan.coverage.length : 0) > 4 && (
                                        <span style={{
                                            fontSize: '0.75rem',
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '6px',
                                            backgroundColor: '#f3f4f6',
                                            color: 'var(--text-muted)'
                                        }}>+more</span>
                                    )}
                                </div>
                            </div>

                            {/* Subscribers Section */}
                            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
                                <p style={{
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    textTransform: 'uppercase',
                                    marginBottom: '0.75rem',
                                    color: 'var(--text-muted)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem'
                                }}>
                                    <Users size={12} /> Subscribers ({subscribers.length})
                                </p>
                                {subscribers.length > 0 ? (
                                    <div style={{ maxHeight: '8rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {subscribers.slice(0, 3).map((subscriber, idx) => (
                                            <div key={idx} style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.5rem',
                                                fontSize: '0.75rem',
                                                padding: '0.5rem',
                                                borderRadius: '6px',
                                                backgroundColor: '#f8fafc'
                                            }}>
                                                <UserCheck size={12} style={{ color: '#059669' }} />
                                                <span style={{ fontWeight: '500', color: 'var(--text)' }}>{subscriber.name}</span>
                                                <span style={{ color: 'var(--text-muted)' }}>({subscriber.username})</span>
                                                {subscriber.role === 'admin' && (
                                                    <span style={{
                                                        fontSize: '0.75rem',
                                                        padding: '0.125rem 0.5rem',
                                                        borderRadius: '4px',
                                                        backgroundColor: '#f3e8ff',
                                                        color: '#7c3aed',
                                                        fontWeight: '500'
                                                    }}>Admin</span>
                                                )}
                                            </div>
                                        ))}
                                        {subscribers.length > 3 && (
                                            <div style={{
                                                fontSize: '0.75rem',
                                                textAlign: 'center',
                                                padding: '0.5rem',
                                                color: 'var(--text-muted)'
                                            }}>
                                                +{subscribers.length - 3} more subscribers
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div style={{ fontSize: '0.75rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                                        No subscribers yet
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default PlanManager;
