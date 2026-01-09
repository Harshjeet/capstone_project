import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const CONDITIONS_LIST = [
    "Hypertension", "Diabetes mellitus", "Asthma", "Acute upper respiratory infection",
    "Fever", "Cough", "Headache", "Coronary heart disease"
];

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        firstName: '',
        lastName: '',
        gender: 'male',
        birthDate: '',
        mobile: '',
        address: '',
        conditions: [], // Multi-select array
        vitals: {
            systolic: '',
            diastolic: '',
            heartRate: '',
            weight: '',
            height: ''
        },
        insuranceProvider: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.startsWith('vital_')) {
            const vitalName = name.split('_')[1];
            setFormData(prev => ({
                ...prev,
                vitals: { ...prev.vitals, [vitalName]: value }
            }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleConditionChange = (e) => {
        const { options } = e.target;
        const selected = [];
        for (let i = 0; i < options.length; i++) {
            if (options[i].selected) {
                selected.push(options[i].value);
            }
        }
        setFormData(prev => ({ ...prev, conditions: selected }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            await axios.post('/auth/register', {
                username: formData.username,
                password: formData.password,
                patientDetails: {
                    firstName: formData.firstName,
                    lastName: formData.lastName,
                    gender: formData.gender,
                    birthDate: formData.birthDate,
                    mobile: formData.mobile,
                    address: formData.address
                },
                conditions: formData.conditions,
                vitals: formData.vitals,
                insuranceProvider: formData.insuranceProvider
            });
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed');
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card register-card">
                <h2>Create Account</h2>
                <p className="auth-subtitle">Join our premium healthcare network</p>

                {error && <div className="alert alert-error">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form grid-form">
                    <div className="form-group full-width">
                        <label>Username</label>
                        <input name="username" value={formData.username} onChange={handleChange} required />
                    </div>
                    <div className="form-group full-width">
                        <label>Password</label>
                        <input type="password" name="password" value={formData.password} onChange={handleChange} required />
                    </div>

                    <div className="form-section-title full-width">Patient Details</div>

                    <div className="form-group">
                        <label>First Name</label>
                        <input name="firstName" value={formData.firstName} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                        <label>Last Name</label>
                        <input name="lastName" value={formData.lastName} onChange={handleChange} required />
                    </div>

                    <div className="form-group">
                        <label>Gender</label>
                        <select name="gender" value={formData.gender} onChange={handleChange}>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Birth Date</label>
                        <input type="date" name="birthDate" value={formData.birthDate} onChange={handleChange} required />
                    </div>

                    <div className="form-group">
                        <label>Mobile</label>
                        <input name="mobile" value={formData.mobile} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                        <label>Address</label>
                        <input name="address" value={formData.address} onChange={handleChange} required />
                    </div>

                    <div className="form-section-title full-width">Health Data (Optional)</div>

                    <div className="form-group full-width">
                        <label>Existing Conditions (Hold Ctrl/Cmd to select multiple)</label>
                        <select
                            multiple
                            name="conditions"
                            className="multi-select"
                            value={formData.conditions}
                            onChange={handleConditionChange}
                        >
                            {CONDITIONS_LIST.map(c => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Systolic BP (mmHg)</label>
                        <input type="number" name="vital_systolic" placeholder="120" value={formData.vitals.systolic} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Diastolic BP (mmHg)</label>
                        <input type="number" name="vital_diastolic" placeholder="80" value={formData.vitals.diastolic} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Heart Rate (bpm)</label>
                        <input type="number" name="vital_heartRate" placeholder="72" value={formData.vitals.heartRate} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Weight (kg)</label>
                        <input type="number" name="vital_weight" placeholder="70" value={formData.vitals.weight} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label>Height (cm)</label>
                        <input type="number" name="vital_height" placeholder="175" value={formData.vitals.height} onChange={handleChange} />
                    </div>

                    <div className="form-section-title full-width">Insurance</div>
                    <div className="form-group full-width">
                        <label>Current Provider</label>
                        <select name="insuranceProvider" value={formData.insuranceProvider} onChange={handleChange}>
                            <option value="">None / Self-pay</option>
                            <option value="Aetna">Aetna</option>
                            <option value="BlueCross">Blue Cross Blue Shield</option>
                            <option value="Cigna">Cigna</option>
                            <option value="UnitedHealth">UnitedHealthcare</option>
                            <option value="Medicare">Medicare</option>
                        </select>
                    </div>

                    <button type="submit" className="btn btn-primary btn-block full-width">Register</button>
                </form>

                <div className="auth-footer">
                    Already have an account? <Link to="/login">Login here</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
