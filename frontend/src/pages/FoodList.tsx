import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Food {
  _id: string;
  name: string;
  description: string;
  price: number;
  category: { _id: string; name: string };
  isAvailable: boolean;
  ingredients: string[];
  allergens: string[];
}

const FoodList: React.FC = () => {
  const [foods, setFoods] = useState<Food[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 0,
    category: '',
    ingredients: '',
    allergens: '',
    isAvailable: true
  });

  useEffect(() => {
    fetchFoods();
    fetchCategories();
  }, []);

  const fetchFoods = async () => {
    try {
      const response = await api.get('/foods');
      setFoods(response.data);
    } catch (error) {
      console.error('Error fetching foods:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/foods', {
        ...formData,
        ingredients: formData.ingredients.split(',').map(i => i.trim()),
        allergens: formData.allergens.split(',').map(a => a.trim())
      });
      setShowForm(false);
      fetchFoods();
      setFormData({
        name: '',
        description: '',
        price: 0,
        category: '',
        ingredients: '',
        allergens: '',
        isAvailable: true
      });
    } catch (error) {
      console.error('Error creating food:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this food item?')) {
      try {
        await api.delete(`/foods/${id}`);
        fetchFoods();
      } catch (error) {
        console.error('Error deleting food:', error);
      }
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px' }}>
        <h1>Food Items</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          {showForm ? 'Cancel' : 'Add New Food'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h2>Add New Food Item</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Price</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                required
              >
                <option value="">Select a category</option>
                {categories.map((cat) => (
                  <option key={cat._id} value={cat._id}>{cat.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Ingredients (comma-separated)</label>
              <input
                type="text"
                value={formData.ingredients}
                onChange={(e) => setFormData({ ...formData, ingredients: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Allergens (comma-separated)</label>
              <input
                type="text"
                value={formData.allergens}
                onChange={(e) => setFormData({ ...formData, allergens: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.isAvailable}
                  onChange={(e) => setFormData({ ...formData, isAvailable: e.target.checked })}
                />
                {' '}Available
              </label>
            </div>
            <button type="submit" className="btn btn-primary">Create Food Item</button>
          </form>
        </div>
      )}

      <div className="card" style={{ marginTop: '20px' }}>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {foods.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '20px' }}>
                  No food items found. Add your first food item to get started.
                </td>
              </tr>
            ) : (
              foods.map((food) => (
                <tr key={food._id}>
                  <td>{food.name}</td>
                  <td>{food.category?.name || 'N/A'}</td>
                  <td>${food.price.toFixed(2)}</td>
                  <td>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: food.isAvailable ? '#d4edda' : '#f8d7da',
                      color: food.isAvailable ? '#155724' : '#721c24'
                    }}>
                      {food.isAvailable ? 'Available' : 'Unavailable'}
                    </span>
                  </td>
                  <td>
                    <button onClick={() => handleDelete(food._id)} className="btn btn-danger">
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FoodList;
