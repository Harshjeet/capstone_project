import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, HeartPulse } from 'lucide-react';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const getHomeLink = () => {
        if (!user) return "/";
        return user.role === 'admin' ? "/admin" : "/dashboard";
    };

    return (
        <nav className="navbar">
            <div className="container navbar-content">
                <Link to={getHomeLink()} className="logo">
                    <HeartPulse size={28} className="logo-icon" />
                    <span>MediCare Premium</span>
                </Link>
                <div className="nav-links">
                    {user ? (
                        <>
                            <span className="user-greeting">Welcome, {user.name}</span>
                            <Link to="/analytics" className="nav-link">Analytics</Link>
                            <button onClick={handleLogout} className="btn btn-outline">
                                <LogOut size={18} /> Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">Login</Link>
                            <Link to="/register" className="btn btn-primary">Get Started</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
