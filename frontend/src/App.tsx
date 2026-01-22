import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FoodList from './pages/FoodList';
import CategoryList from './pages/CategoryList';
import Login from './pages/Login';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);

  React.useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <Router>
      <div style={{ minHeight: '100vh' }}>
        <nav style={{
          backgroundColor: '#333',
          color: 'white',
          padding: '1rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ margin: 0 }}>FoodBeverages CMS</h1>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
            <Link to="/foods" style={{ color: 'white', textDecoration: 'none' }}>Foods</Link>
            <Link to="/categories" style={{ color: 'white', textDecoration: 'none' }}>Categories</Link>
            <button onClick={handleLogout} className="btn btn-danger">Logout</button>
          </div>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/foods" element={<FoodList />} />
            <Route path="/categories" element={<CategoryList />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
