import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    DoughnutController,
    PointElement,
    LineElement
} from 'chart.js';
import { Bar, Pie, Doughnut } from 'react-chartjs-2';
import { MapPin, Users, Activity, ShieldAlert, Pill, Heart, Zap } from 'lucide-react';

ChartJS.register(
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    DoughnutController,
    PointElement,
    LineElement
);

const AdminAnalytics = () => {
    const [trends, setTrends] = useState(null);
    const [ageTrends, setAgeTrends] = useState([]);
    const [riskDist, setRiskDist] = useState(null);
    const [chronicAcute, setChronicAcute] = useState([]);
    const [medicationData, setMedicationData] = useState({ by_disease: [], unique_usage: [] });
    const [vitalsData, setVitalsData] = useState([]);
    const [locationFilter, setLocationFilter] = useState('');
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [trendsRes, ageRes, riskRes, caRes, medRes, vitRes] = await Promise.all([
                axios.get(`/stats/trends?location=${locationFilter}`),
                axios.get('/stats/disease-trends-by-age'),
                axios.get('/admin/stats/risk-distribution'),
                axios.get('/analytics/population/chronic-acute'),
                axios.get('/analytics/population/medications'),
                axios.get('/analytics/population/vitals')
            ]);
            setTrends(trendsRes.data);
            setAgeTrends(ageRes.data);
            setRiskDist(riskRes.data);
            setChronicAcute(caRes.data);
            setMedicationData(medRes.data);
            setVitalsData(vitRes.data);
        } catch (err) {
            console.error("Failed to fetch admin stats", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(fetchData, 800);
        return () => clearTimeout(timer);
    }, [locationFilter]);

    if (!trends || !riskDist || loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '1rem' }}>
            <div className="spinner" style={{ width: '40px', height: '40px', border: '4px solid #f3f3f3', borderTop: '4px solid var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
            <p style={{ color: 'var(--text-muted)' }}>Analyzing population health data...</p>
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        </div>
    );

    // Data Preparation
    const hasConditionData = trends.top_conditions && trends.top_conditions.length > 0;

    const conditionData = {
        labels: hasConditionData ? trends.top_conditions.map(i => i.name) : ['No Data'],
        datasets: [{
            label: 'Patient Count',
            data: hasConditionData ? trends.top_conditions.map(i => i.value) : [1],
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
            borderWidth: 0,
            hoverOffset: 15
        }]
    };

    const riskData = {
        labels: riskDist.labels,
        datasets: [{
            data: riskDist.data,
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'], // Green, Orange, Red
            borderWidth: 0,
            cutout: '75%',
            hoverOffset: 10
        }]
    };

    // Chronic vs Acute
    const caCounts = chronicAcute.reduce((acc, curr) => {
        acc[curr.type] = (acc[curr.type] || 0) + curr.count;
        return acc;
    }, { Chronic: 0, Acute: 0 });

    const chronicAcuteData = {
        labels: ['Chronic', 'Acute'],
        datasets: [{
            data: [caCounts.Chronic, caCounts.Acute],
            backgroundColor: ['#8B5CF6', '#10B981'],
            borderWidth: 0
        }]
    };

    // Medication Usage - Show top medication counts
    const sortedMedUsage = [...(medicationData.unique_usage || [])].sort((a, b) => b.count - a.count).slice(0, 8);

    const medicationChartData = {
        labels: sortedMedUsage.map(m => m.medication),
        datasets: [{
            label: 'Total Patients',
            data: sortedMedUsage.map(m => m.count),
            backgroundColor: 'rgba(245, 158, 11, 0.8)',
            borderRadius: 8,
            barThickness: 20
        }]
    };

    // Age Group Bar Chart
    const ageGroupLabels = ageTrends.map(g => g.age_group);
    const ageGroupData = {
        labels: ageGroupLabels,
        datasets: [
            {
                label: 'Cases',
                data: ageTrends.map(g => g.top_diseases.reduce((sum, d) => sum + d.value, 0)),
                backgroundColor: 'rgba(79, 70, 229, 0.7)',
                borderRadius: 8,
            }
        ]
    };

    // Vitals by Age
    const vitalLabels = [...new Set(vitalsData.map(v => v.age_group))].sort();
    const vitalTypes = [...new Set(vitalsData.map(v => v.vital))];
    const vitalsChartData = {
        labels: vitalLabels,
        datasets: vitalTypes.map((type, i) => ({
            label: type,
            data: vitalLabels.map(group => {
                const item = vitalsData.find(v => v.vital === type && v.age_group === group);
                return item ? item.count : 0;
            }),
            backgroundColor: i === 0 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(59, 130, 246, 0.8)',
            borderRadius: 6,
        }))
    };

    return (
        <div className="admin-analytics-wrapper" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
                    <div>
                        <h2 style={{ fontSize: '2.25rem', fontWeight: '800', color: '#1e293b', marginBottom: '0.5rem', letterSpacing: '-0.025em' }}>
                            Intelligence Command
                        </h2>
                        <p style={{ color: '#64748b', fontSize: '1.125rem' }}>Real-time population health metrics and risk stratifications.</p>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <div style={{ position: 'relative' }}>
                            <MapPin style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} size={18} />
                            <input
                                type="text"
                                placeholder="Filter by region..."
                                value={locationFilter}
                                onChange={(e) => setLocationFilter(e.target.value)}
                                style={{
                                    padding: '0.75rem 1rem 0.75rem 2.75rem',
                                    border: '1px solid #e2e8f0',
                                    borderRadius: '12px',
                                    backgroundColor: 'white',
                                    fontSize: '0.875rem',
                                    width: '240px',
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                                    outline: 'none',
                                    transition: 'all 0.2s'
                                }}
                                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                                onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                            />
                        </div>
                        <button
                            onClick={fetchData}
                            style={{
                                padding: '0.75rem',
                                borderRadius: '12px',
                                border: '1px solid #e2e8f0',
                                background: 'white',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <Zap size={18} style={{ color: 'var(--primary)' }} />
                        </button>
                    </div>
                </div>

                {/* Key Metrics Row */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                    <MetricCard icon={Users} label="Total Patients" value={riskDist.data.reduce((a, b) => a + b, 0)} color="#3b82f6" />
                    <MetricCard icon={Activity} label="Active Conditions" value={trends.total_conditions_count || 0} color="#10b981" />
                    <MetricCard icon={Heart} label="Abnormal Vitals" value={vitalsData.reduce((a, b) => a + b.count, 0)} color="#ef4444" />
                    <MetricCard icon={ShieldAlert} label="High Risk" value={riskDist.data[2]} color="#dc2626" />
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem' }}>

                {/* Condition Distribution - Large Pie */}
                <div className="card" style={{ gridColumn: 'span 4', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#dbeafe', color: '#2563eb', borderRadius: '10px' }}>
                            <Activity size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Prevalent Conditions</h3>
                    </div>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <Pie data={conditionData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
                    </div>
                </div>

                {/* Risk Distribution - Doughnut */}
                <div className="card" style={{ gridColumn: 'span 4', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#fee2e2', color: '#dc2626', borderRadius: '10px' }}>
                            <ShieldAlert size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Risk Stratification</h3>
                    </div>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <Doughnut data={riskData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
                        <div style={{
                            position: 'absolute',
                            inset: '0 0 40px 0',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexDirection: 'column',
                            pointerEvents: 'none'
                        }}>
                            <span style={{ fontSize: '2.5rem', fontWeight: '800', color: '#1e293b' }}>{riskDist.data.reduce((a, b) => a + b, 0)}</span>
                            <span style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Patients</span>
                        </div>
                    </div>
                </div>

                {/* Chronic vs Acute - Small Pie */}
                <div className="card" style={{ gridColumn: 'span 4', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#f3e8ff', color: '#9333ea', borderRadius: '10px' }}>
                            <Activity size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Chronic vs Acute</h3>
                    </div>
                    <div style={{ flex: 1 }}>
                        <Pie data={chronicAcuteData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
                    </div>
                </div>

                {/* Medication Usage - Horizontal Bar */}
                <div className="card" style={{ gridColumn: 'span 6', minHeight: '400px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#fef3c7', color: '#d97706', borderRadius: '10px' }}>
                            <Pill size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Therapeutic Utilization</h3>
                    </div>
                    <div style={{ height: '300px' }}>
                        <Bar
                            data={medicationChartData}
                            options={{
                                indexAxis: 'y',
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: { x: { grid: { display: false } }, y: { grid: { display: false } } }
                            }}
                        />
                    </div>
                </div>

                {/* Age Group Trends - Bar Chart */}
                <div className="card" style={{ gridColumn: 'span 6', minHeight: '400px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#e0e7ff', color: '#4f46e5', borderRadius: '10px' }}>
                            <Users size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Age Demographics</h3>
                    </div>
                    <div style={{ height: '300px' }}>
                        <Bar
                            data={ageGroupData}
                            options={{
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: { x: { grid: { display: false } }, y: { grid: { display: false } } }
                            }}
                        />
                    </div>
                </div>

                {/* Vital Trends by Age - Stacked Bar */}
                <div className="card" style={{ gridColumn: 'span 12', minHeight: '450px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ padding: '0.6rem', backgroundColor: '#fee2e2', color: '#ef4444', borderRadius: '10px' }}>
                            <Heart size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.125rem', fontWeight: '700', margin: '0' }}>Clinical Observation Anomalies</h3>
                    </div>
                    <div style={{ height: '350px' }}>
                        <Bar
                            data={vitalsChartData}
                            options={{
                                maintainAspectRatio: false,
                                scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, grid: { color: '#f1f5f9' } } }
                            }}
                        />
                    </div>
                </div>

            </div>

            <style>{`
                .admin-analytics-wrapper .card {
                    background: white;
                    border-radius: 16px;
                    padding: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                    border: 1px solid #f1f5f9;
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .admin-analytics-wrapper .card:hover {
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
                }
            `}</style>
        </div>
    );
};

const MetricCard = ({ icon: Icon, label, value, color }) => (
    <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '16px',
        border: '1px solid #f1f5f9',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
    }}>
        <div style={{ padding: '0.75rem', backgroundColor: `${color}15`, color: color, borderRadius: '12px' }}>
            <Icon size={24} />
        </div>
        <div>
            <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem', fontWeight: '600' }}>{label}</p>
            <h4 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '800', color: '#1e293b' }}>{value}</h4>
        </div>
    </div>
);

export default AdminAnalytics;
