import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import { User, MapPin, Calendar, Activity, Pill, Heart } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
// Reusing dashboard styles via local style block below

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

export default function Analytics() {
    const [trends, setTrends] = useState({ top_conditions: [], patient_demographics: [] });
    const [chronicAcute, setChronicAcute] = useState([]);
    const [vitalsData, setVitalsData] = useState([]);
    const [medicationData, setMedicationData] = useState({ by_age: [], by_disease: [] });
    const { user } = useAuth();

    // Filter States
    const [location, setLocation] = useState('');
    const [ageMin, setAgeMin] = useState('');
    const [ageMax, setAgeMax] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchAnalytics = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (location) params.append('location', location);
            if (ageMin) params.append('age_min', ageMin);
            if (ageMax) params.append('age_max', ageMax);

            // Fetch Population Trends (Filtered)
            const res = await axios.get(`/stats/trends?${params.toString()}`);
            setTrends(res.data);

            // Fetch Advanced Analytics (Population Level)
            const caRes = await axios.get('/analytics/population/chronic-acute');
            setChronicAcute(caRes.data);

            // Fetch Medication and Vitals (Admin Only)
            if (user?.role === 'admin') {
                const [vRes, mRes] = await Promise.all([
                    axios.get('/analytics/population/vitals'),
                    axios.get('/analytics/population/medications')
                ]);
                setVitalsData(vRes.data);
                setMedicationData(mRes.data);
            }

        } catch (err) {
            console.error("Failed to fetch analytics", err);
        } finally {
            setLoading(false);
        }
    };

    // Debounce fetch to avoid too many requests while typing
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchAnalytics();
        }, 800);
        return () => clearTimeout(timer);
    }, [location, ageMin, ageMax]);

    const conditionsData = {
        labels: trends.top_conditions.map(c => c.name),
        datasets: [{
            label: '# of Cases',
            data: trends.top_conditions.map(c => c.value),
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
            ],
            borderWidth: 1,
        }],
    };

    const genderData = {
        labels: trends.patient_demographics.map(d => d.name),
        datasets: [{
            label: 'Gender Distribution',
            data: trends.patient_demographics.map(d => d.value),
            backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
        }],
    };

    // 1. Chronic vs Acute (Pie Chart)
    const caCounts = chronicAcute.reduce((acc, curr) => {
        acc[curr.type] = (acc[curr.type] || 0) + curr.count;
        return acc;
    }, {});
    const chronicAcuteData = {
        labels: Object.keys(caCounts),
        datasets: [{
            data: Object.values(caCounts),
            backgroundColor: ['#8B5CF6', '#10B981', '#6B7280'],
        }]
    };

    const medicationChartData = {
        labels: Object.keys(medicationData.by_disease.reduce((acc, curr) => {
            acc[curr.medication] = (acc[curr.medication] || 0) + curr.count;
            return acc;
        }, {})),
        datasets: [{
            label: 'Number of Patients',
            data: Object.values(medicationData.by_disease.reduce((acc, curr) => {
                acc[curr.medication] = (acc[curr.medication] || 0) + curr.count;
                return acc;
            }, {})),
            backgroundColor: '#F59E0B',
            borderRadius: 6,
        }]
    };

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
            backgroundColor: i === 0 ? '#EF4444' : '#3B82F6',
            borderRadius: 6,
        }))
    };

    const medCounts = medicationData.by_disease.reduce((acc, curr) => {
        acc[curr.medication] = (acc[curr.medication] || 0) + curr.count;
        return acc;
    }, {});

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div>
                    <h1>Health & Disease Analytics</h1>
                    <p>Explore real-time health trends by location and age.</p>
                </div>
            </header>

            {/* Filter Section */}
            <div className="analytics-filters">
                <div className="filter-group">
                    <MapPin size={18} />
                    <input
                        type="text"
                        placeholder="Location (e.g. New York)"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                    />
                </div>
                <div className="filter-group">
                    <Calendar size={18} />
                    <input
                        type="number"
                        placeholder="Min Age"
                        value={ageMin}
                        onChange={(e) => setAgeMin(e.target.value)}
                        className="age-input"
                    />
                    <span>-</span>
                    <input
                        type="number"
                        placeholder="Max Age"
                        value={ageMax}
                        onChange={(e) => setAgeMax(e.target.value)}
                        className="age-input"
                    />
                </div>
            </div>

            {loading && <div className="loading-spinner">Updating Data...</div>}

            <div className="charts-grid analytics-full-grid">
                {/* Row 1: Top Conditions & Demographics */}
                <div className="chart-card">
                    <div className="chart-header">
                        <Activity className="icon" />
                        <h2>Top Conditions</h2>
                    </div>
                    {trends.top_conditions.length > 0 ? (
                        <div className="chart-wrapper pie-wrapper">
                            <Pie data={conditionsData} options={{ maintainAspectRatio: false }} />
                        </div>
                    ) : (
                        <p className="no-data">No data found.</p>
                    )}
                </div>

                <div className="chart-card">
                    <div className="chart-header">
                        <User className="icon" />
                        <h2>Demographics</h2>
                    </div>
                    {trends.patient_demographics.length > 0 ? (
                        <div className="chart-wrapper">
                            <Bar data={genderData} options={{ indexAxis: 'y', maintainAspectRatio: false }} />
                        </div>
                    ) : (
                        <p className="no-data">No data found.</p>
                    )}
                </div>

                <div className="chart-card full-width-chart">
                    <div className="chart-header">
                        <Activity className="icon" />
                        <h2>Chronic vs Acute</h2>
                    </div>
                    {chronicAcute.length > 0 ? (
                        <div className="chart-wrapper pie-wrapper">
                            <Pie data={chronicAcuteData} options={{ maintainAspectRatio: false }} />
                        </div>
                    ) : (
                        <p className="no-data">No condition type data found.</p>
                    )}
                </div>

                {/* Admin Only Row: Medication & Vitals */}
                {user?.role === 'admin' && (
                    <>
                        <div className="chart-card">
                            <div className="chart-header">
                                <Pill className="icon" />
                                <h2>Medication Usage</h2>
                            </div>
                            {Object.keys(medCounts).length > 0 ? (
                                <div className="chart-wrapper">
                                    <Bar
                                        data={medicationChartData}
                                        options={{
                                            indexAxis: 'y',
                                            maintainAspectRatio: false,
                                            plugins: {
                                                title: { display: true, text: 'Total Patients per Medication' }
                                            }
                                        }}
                                    />
                                </div>
                            ) : (
                                <p className="no-data">No medication data found.</p>
                            )}
                        </div>

                        <div className="chart-card">
                            <div className="chart-header">
                                <Heart className="icon" />
                                <h2>Abnormal Vitals by Age</h2>
                            </div>
                            {vitalsData.length > 0 ? (
                                <div className="chart-wrapper">
                                    <Bar
                                        data={vitalsChartData}
                                        options={{
                                            maintainAspectRatio: false,
                                            scales: {
                                                x: { stacked: true },
                                                y: { stacked: true }
                                            }
                                        }}
                                    />
                                </div>
                            ) : (
                                <p className="no-data">No vitals data found.</p>
                            )}
                        </div>
                    </>
                )}
            </div>

            <style>{`
                .analytics-full-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                .full-width-chart {
                    grid-column: span 2;
                }
                .chart-wrapper {
                    height: 250px;
                    position: relative;
                }
                .pie-wrapper {
                    height: 200px;
                }
                .large-chart {
                    height: 350px;
                }
                .analytics-filters {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 30px;
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    align-items: center;
                }
                .filter-group {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: #555;
                }
                .filter-group input {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s;
                }
                .filter-group input:focus {
                    border-color: #4facfe;
                    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
                }
                .age-input {
                    width: 80px;
                }
                .loading-spinner {
                    text-align: center;
                    color: #666;
                    margin: 10px;
                    font-style: italic;
                }
                .no-data {
                    text-align: center;
                    padding: 40px;
                    color: #999;
                }
            `}</style>
        </div>
    );
}
