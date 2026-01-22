import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1 style={{ marginTop: '20px' }}>Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <h3>Total Foods</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#007bff' }}>-</p>
          <p style={{ color: '#666' }}>Manage your food items</p>
        </div>
        <div className="card">
          <h3>Categories</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>-</p>
          <p style={{ color: '#666' }}>Organize by category</p>
        </div>
        <div className="card">
          <h3>Available Items</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ffc107' }}>-</p>
          <p style={{ color: '#666' }}>Currently in stock</p>
        </div>
      </div>
      <div className="card" style={{ marginTop: '20px' }}>
        <h2>Welcome to FoodBeverages CMS</h2>
        <p>Manage your food and beverage inventory with ease.</p>
        <ul>
          <li>Create and manage food items with detailed information</li>
          <li>Organize items by categories</li>
          <li>Track nutritional information and allergens</li>
          <li>Control availability and pricing</li>
          <li>Role-based access control for your team</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
