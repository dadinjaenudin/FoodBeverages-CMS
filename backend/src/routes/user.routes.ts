import { Router } from 'express';
import { register, login, getAllUsers } from '../controllers/user.controller';
import { authenticateToken, authorizeRole } from '../middleware/auth';

const router = Router();

// Public routes
router.post('/register', register);
router.post('/login', login);

// Protected routes
router.get('/', authenticateToken, authorizeRole('admin'), getAllUsers);

export default router;
