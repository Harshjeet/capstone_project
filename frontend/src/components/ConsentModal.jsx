import { useState } from 'react';
import axios from 'axios';
import { Shield, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const ConsentModal = ({ onConsentGiven }) => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleAccept = async () => {
        setLoading(true);
        try {
            const consentData = {
                resourceType: "Consent",
                status: "active",
                scope: {
                    coding: [{
                        system: "http://terminology.hl7.org/CodeSystem/consentscope",
                        code: "patient-privacy",
                        display: "Privacy Consent"
                    }]
                },
                category: [{
                    coding: [{
                        system: "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        code: "INFA",
                        display: "information access"
                    }]
                }],
                patient: {
                    reference: `Patient/${user.patientId}`
                },
                dateTime: new Date().toISOString(),
                policyRule: {
                    coding: [{
                        system: "http://terminology.hl7.org/CodeSystem/consentpolicycodes",
                        code: "opt-in",
                        display: "Opt-in to data usage"
                    }]
                }
            };

            await axios.post('/Consent', consentData);
            if (onConsentGiven) onConsentGiven();
        } catch (err) {
            console.error(err);
            setError('Failed to record consent. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <Shield size={48} className="text-primary" />
                    <h2>Data Usage Consent</h2>
                </div>
                <div className="modal-body">
                    <p>
                        To provide you with personalized health insights and insurance recommendations,
                        we need your permission to analyze your health data.
                    </p>
                    <ul className="consent-list">
                        <li><CheckCircle size={16} /> Analyze conditions for risk scoring</li>
                        <li><CheckCircle size={16} /> Match with similar patient cohorts</li>
                        <li><CheckCircle size={16} /> Recommend insurance plans</li>
                    </ul>
                    <p className="legal-text">
                        Your data is processed securely and in accordance with FHIR standards.
                    </p>
                    {error && <div className="alert alert-error">{error}</div>}
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" disabled={loading}>Decline</button>
                    <button className="btn btn-primary" onClick={handleAccept} disabled={loading}>
                        {loading ? 'Processing...' : 'I Agree'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConsentModal;
