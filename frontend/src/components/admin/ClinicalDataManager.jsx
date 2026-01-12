import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DataTable from '../DataTable';

const ClinicalDataManager = () => {
    const [conditions, setConditions] = useState([]);
    const [observations, setObservations] = useState([]);
    const [medications, setMedications] = useState([]);
    const [risks, setRisks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [condRes, obsRes, medRes, riskRes] = await Promise.all([
                    axios.get('/admin/clinical/conditions'),
                    axios.get('/admin/clinical/observations'),
                    axios.get('/admin/clinical/medications'),
                    axios.get('/admin/clinical/risk-assessments')
                ]);
                setConditions(condRes.data);
                setObservations(obsRes.data);
                setMedications(medRes.data);
                setRisks(riskRes.data);
            } catch (error) {
                console.error("Error fetching clinical data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="dashboard-container">
            <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text)' }}>Clinical Data Registry</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Centralized view of medical conditions, observations, and medications.</p>

            <DataTable
                title="Conditions"
                data={conditions.map(c => ({
                    ...c,
                    code: c.code?.text,
                    clinicalStatus: c.clinicalStatus?.text,
                    subject: c.subject?.reference
                }))}
                columns={['code', 'clinicalStatus', 'subject']}
                isLoading={loading}
            />

            <DataTable
                title="Observations (Vitals)"
                data={observations.map(o => ({
                    ...o,
                    code: o.code?.text,
                    value: o.valueQuantity ? `${o.valueQuantity.value} ${o.valueQuantity.unit}` : 'N/A',
                    subject: o.subject?.reference
                }))}
                columns={['code', 'value', 'subject']}
                isLoading={loading}
            />

            <DataTable
                title="Prescribed Medications"
                data={medications.map(m => ({
                    ...m,
                    medication: m.medicationCodeableConcept?.text || "Unknown",
                    dosage: m.dosageInstruction?.[0]?.text || "N/A",
                    subject: m.subject?.reference
                }))}
                columns={['medication', 'dosage', 'subject']}
                isLoading={loading}
            />

            <DataTable
                title="Risk Assessments (AI Predictions)"
                data={risks.map(r => ({
                    ...r,
                    date: new Date(r.occurrenceDateTime).toLocaleString(),
                    prediction: r.prediction?.[0]?.qualitativeRisk?.coding?.[0]?.display || "Unknown",
                    probability: r.prediction?.[0]?.probabilityDecimal || "0",
                    subject: r.subject?.reference
                }))}
                columns={['date', 'prediction', 'probability', 'subject']}
                isLoading={loading}
            />
        </div>
    );
};

export default ClinicalDataManager;
