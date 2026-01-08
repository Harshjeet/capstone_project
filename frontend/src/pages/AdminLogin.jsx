import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminLogin = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('/auth/login', { username, password });

            if (res.data.role !== 'admin') {
                setError("Access Denied. Not an admin account.");
                return;
            }

            login(res.data);
            navigate('/admin');
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h2>Admin Portal</h2>
                <p className="auth-subtitle">Enter your credentials to access the dashboard</p>

                {error && <div className="alert alert-error">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="Enter admin ID"
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>
                    <button type="submit" className="btn btn-primary btn-block">Sign In</button>
                </form>

                <div className="auth-footer">
                    <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
                        <strong>Restricted Access System</strong>
                    </span>
                </div>
            </div>
        </div>
    );
};

export default AdminLogin;
