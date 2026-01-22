import { Router } from 'express';
import {
  getAllFoods,
  getFoodById,
  createFood,
  updateFood,
  deleteFood
} from '../controllers/food.controller';
import { authenticateToken, authorizeRole } from '../middleware/auth';

const router = Router();

// Public routes
router.get('/', getAllFoods);
router.get('/:id', getFoodById);

// Protected routes (require authentication and authorization)
router.post('/', authenticateToken, authorizeRole('admin', 'manager'), createFood);
router.put('/:id', authenticateToken, authorizeRole('admin', 'manager'), updateFood);
router.delete('/:id', authenticateToken, authorizeRole('admin'), deleteFood);

export default router;
