import { Router } from 'express';
import {
  getAllCategories,
  getCategoryById,
  createCategory,
  updateCategory,
  deleteCategory
} from '../controllers/category.controller';
import { authenticateToken, authorizeRole } from '../middleware/auth';

const router = Router();

// Public routes
router.get('/', getAllCategories);
router.get('/:id', getCategoryById);

// Protected routes
router.post('/', authenticateToken, authorizeRole('admin', 'manager'), createCategory);
router.put('/:id', authenticateToken, authorizeRole('admin', 'manager'), updateCategory);
router.delete('/:id', authenticateToken, authorizeRole('admin'), deleteCategory);

export default router;
