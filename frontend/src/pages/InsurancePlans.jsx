import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Check, Users } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const InsurancePlans = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [data, setData] = useState(null);
    const [activeCoverages, setActiveCoverages] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [selectedPlanId, setSelectedPlanId] = useState(location.state?.preSelectedPlanId || null);

    useEffect(() => {
        const fetchData = async () => {
            if (!user?.patientId) return;
            try {
                const [recRes, covRes] = await Promise.all([
                    axios.post(`/recommendation/${user.patientId}`),
                    axios.get(`/Coverage?patient=${user.patientId}`)
                ]);
                setData(recRes.data);
                setActiveCoverages(covRes.data);
            } catch (err) {
                console.error("Failed to fetch insurance data", err);
            }
        };
        fetchData();
    }, [user]);

    const isPlanActive = (planId) => {
        return activeCoverages.some(c => c.class?.[0]?.value === planId && c.status === 'active');
    };

    const handleSelectPlan = async (plan) => {
        if (isPlanActive(plan.id)) {
            alert("You already have this plan active!");
            return;
        }

        setProcessing(true);
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
            navigate('/dashboard');
        } catch (err) {
            console.error(err);
            alert("Enrollment failed.");
        } finally {
            setProcessing(false);
        }
    };

    if (!data) return <div className="loading">Loading plans...</div>;

    const { recommended_plan, all_plans, similar_cohort_size } = data;

    return (
        <div className="dashboard-container">
            <header className="page-header">
                <h1>Insurance Recommendations</h1>
                <p>Based on your risk profile ({data.risk_label}) and similar patients.</p>
            </header>

            <div className="plans-layout">
                {/* Recommended Section */}
                <div className="recommended-section">
                    <div className={`card highlight-card large-card ${isPlanActive(recommended_plan.id) ? 'active-plan' : ''}`}>
                        <div className="card-badge">
                            {isPlanActive(recommended_plan.id) ? 'ACTIVE' : 'RECOMMENDED FOR YOU'}
                        </div>
                        <div className="rec-header">
                            <ShieldCheck size={32} />
                            <div>
                                <h2>{recommended_plan.name}</h2>
                                <p className="rec-reason">
                                    <Users size={16} /> Popular among {similar_cohort_size} similar patients
                                </p>
                            </div>
                            <div className="price-tag">
                                ${recommended_plan.cost}<span>/mo</span>
                            </div>
                        </div>

                        <div className="rec-body">
                            <p>{recommended_plan.description}</p>
                            <div className="coverage-tags">
                                {recommended_plan.coverage.map(c => (
                                    <span key={c} className="tag">{c}</span>
                                ))}
                            </div>
                        </div>

                        <button
                            className={`btn ${isPlanActive(recommended_plan.id) ? 'btn-success' : 'btn-white'} btn-lg`}
                            onClick={() => handleSelectPlan(recommended_plan)}
                            disabled={processing || isPlanActive(recommended_plan.id)}
                        >
                            {isPlanActive(recommended_plan.id) ? (
                                <><Check size={20} /> Currently Enrolled</>
                            ) : (selectedPlanId === recommended_plan.id ? 'Recommended Plan Selected' : 'Select Recommended Plan')}
                        </button>
                    </div>
                </div>

                <div className="all-plans-grid">
                    <h3>All Available Plans</h3>
                    <div className="plans-grid">
                        {all_plans.filter(p => p.id !== recommended_plan.id).map(plan => {
                            const active = isPlanActive(plan.id);
                            return (
                                <div key={plan.id} className={`card plan-card ${active ? 'active-plan' : ''} ${selectedPlanId === plan.id ? 'selected-plan' : ''}`}>
                                    <div className="plan-header">
                                        <h4>{plan.name} {active && <Check size={16} color="var(--success)" />}</h4>
                                        <div className="plan-price">${plan.cost}/mo</div>
                                    </div>
                                    <p className="plan-desc-sm">{plan.description}</p>
                                    <button
                                        className={`btn ${active ? 'btn-success' : 'btn-outline'}`}
                                        onClick={() => handleSelectPlan(plan)}
                                        disabled={processing || active}
                                    >
                                        {active ? 'Enrolled' : 'Select'}
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};


export default InsurancePlans;
