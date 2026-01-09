import { Link } from 'react-router-dom';
import { HeartPulse, ShieldCheck, Activity } from 'lucide-react';

const Home = () => {
    return (
        <div className="home-container">
            <div className="hero-section">
                <div className="hero-content">
                    <div className="hero-badge">
                        <HeartPulse size={16} />
                        <span>AI-Powered Healthcare</span>
                    </div>
                    <h1>Your Health, <span className="text-gradient"> reimagined.</span></h1>
                    <p className="hero-subtitle">
                        Advanced clinical analytics, personalized risk assessments, and smart insurance recommendations—all in one place.
                    </p>
                    <div className="hero-buttons">
                        <Link to="/register" className="btn btn-primary btn-lg">Get Started</Link>
                        <Link to="/login" className="btn btn-outline btn-lg">Login</Link>
                    </div>
                </div>
            </div>

            <div className="features-grid container">
                <div className="feature-card">
                    <div className="feature-icon icon-blue">
                        <Activity />
                    </div>
                    <h3>Smart Analytics</h3>
                    <p>Track disease trends and demographics with our advanced real-time dashboard.</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon icon-green">
                        <ShieldCheck />
                    </div>
                    <h3>Risk Assessment</h3>
                    <p>Get instant risk scores based on your medical history and age profile.</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon icon-purple">
                        <HeartPulse />
                    </div>
                    <h3>Insurance Matching</h3>
                    <p>Receive personalized insurance plan recommendations tailored to your needs.</p>
                </div>
            </div>

            <style>{`
                .home-container {
                    padding-bottom: 4rem;
                }
                .hero-section {
                    background: linear-gradient(180deg, rgba(235, 248, 255, 0.5) 0%, rgba(255, 255, 255, 0) 100%);
                    padding: 6rem 2rem 4rem;
                    text-align: center;
                }
                .hero-content {
                    max-width: 800px;
                    margin: 0 auto;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .hero-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    color: var(--primary);
                    font-weight: 500;
                    margin-bottom: 2rem;
                    border: 1px solid rgba(14, 165, 233, 0.1);
                }
                h1 {
                    font-size: 3.5rem;
                    line-height: 1.1;
                    margin-bottom: 1.5rem;
                    letter-spacing: -0.02em;
                }
                .text-gradient {
                    background: linear-gradient(to right, var(--primary), var(--secondary));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .hero-subtitle {
                    font-size: 1.25rem;
                    color: var(--text-muted);
                    margin-bottom: 2.5rem;
                    max-width: 600px;
                }
                .hero-buttons {
                    display: flex;
                    gap: 1rem;
                }
                .btn-lg {
                    padding: 0.875rem 2rem;
                    font-size: 1rem;
                }
                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin-top: 4rem;
                }
                .feature-card {
                    background: white;
                    padding: 2rem;
                    border-radius: 16px;
                    border: 1px solid #f1f5f9;
                    transition: transform 0.2s;
                }
                .feature-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
                }
                .feature-icon {
                    width: 48px;
                    height: 48px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 12px;
                    margin-bottom: 1.5rem;
                }
                .icon-blue { background: #e0f2fe; color: #0ea5e9; }
                .icon-green { background: #dcfce7; color: #22c55e; }
                .icon-purple { background: #f3e8ff; color: #a855f7; }
                
                h3 { margin-bottom: 0.5rem; font-size: 1.25rem; }
                p { color: var(--text-muted); line-height: 1.6; }
            `}</style>
        </div>
    );
};

export default Home;
