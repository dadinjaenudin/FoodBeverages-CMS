import request from 'supertest';
import app from '../index';

describe('API Health Check', () => {
  it('should return welcome message on root endpoint', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('message');
    expect(response.body.message).toBe('Welcome to FoodBeverages CMS API');
  });
});
