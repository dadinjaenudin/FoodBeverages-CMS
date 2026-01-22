import { Request, Response } from 'express';
import Food from '../models/Food';
import { AuthRequest } from '../middleware/auth';

export const getAllFoods = async (req: Request, res: Response) => {
  try {
    const foods = await Food.find().populate('category', 'name');
    res.json(foods);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getFoodById = async (req: Request, res: Response) => {
  try {
    const food = await Food.findById(req.params.id).populate('category', 'name');
    if (!food) {
      return res.status(404).json({ error: 'Food item not found' });
    }
    res.json(food);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const createFood = async (req: AuthRequest, res: Response) => {
  try {
    const food = new Food(req.body);
    await food.save();
    res.status(201).json(food);
  } catch (error: any) {
    res.status(400).json({ error: error.message });
  }
};

export const updateFood = async (req: Request, res: Response) => {
  try {
    const food = await Food.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!food) {
      return res.status(404).json({ error: 'Food item not found' });
    }
    res.json(food);
  } catch (error: any) {
    res.status(400).json({ error: error.message });
  }
};

export const deleteFood = async (req: Request, res: Response) => {
  try {
    const food = await Food.findByIdAndDelete(req.params.id);
    if (!food) {
      return res.status(404).json({ error: 'Food item not found' });
    }
    res.json({ message: 'Food item deleted successfully' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};
