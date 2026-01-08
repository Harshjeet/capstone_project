import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import PatientDashboard from './pages/PatientDashboard';
import Analytics from './pages/Analytics';
import Home from './pages/Home';
import InsurancePlans from './pages/InsurancePlans';
import AdminLogin from './pages/AdminLogin';

const ProtectedRoute = ({ children, role }) => {
  const { user } = useAuth();
  if (!user) {
    if (role === 'admin') return <Navigate to="/admin/login" />;
    return <Navigate to="/login" />;
  }
  if (role && user.role !== role) {
    if (user.role === 'admin') return <Navigate to="/admin" />;
    return <Navigate to="/" />;
  }
  return children;
};

const PublicRoute = ({ children }) => {
  const { user } = useAuth();
  if (user) {
    if (user.role === 'admin') return <Navigate to="/admin" />;
    return <Navigate to="/dashboard" />;
  }
  return children;
};

const HomeRoute = ({ children }) => {
  const { user } = useAuth();
  if (user) {
    if (user.role === 'admin') return <Navigate to="/admin" />;
    return <Navigate to="/dashboard" />;
  }
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <div className="main-content">
          <Routes>
            <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

            <Route path="/admin/login" element={<PublicRoute><AdminLogin /></PublicRoute>} />

            <Route
              path="/admin"
              element={
                <ProtectedRoute role="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute role="patient">
                  <PatientDashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />

            <Route
              path="/insurance-plans"
              element={
                <ProtectedRoute>
                  <InsurancePlans />
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<HomeRoute><Home /></HomeRoute>} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
