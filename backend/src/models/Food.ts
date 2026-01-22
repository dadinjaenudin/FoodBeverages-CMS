import mongoose, { Schema, Document } from 'mongoose';

export interface IFood extends Document {
  name: string;
  description: string;
  price: number;
  category: mongoose.Types.ObjectId;
  image?: string;
  ingredients: string[];
  allergens: string[];
  nutritionalInfo?: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  isAvailable: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const FoodSchema: Schema = new Schema(
  {
    name: {
      type: String,
      required: [true, 'Food name is required'],
      trim: true
    },
    description: {
      type: String,
      required: [true, 'Description is required'],
      trim: true
    },
    price: {
      type: Number,
      required: [true, 'Price is required'],
      min: 0
    },
    category: {
      type: Schema.Types.ObjectId,
      ref: 'Category',
      required: [true, 'Category is required']
    },
    image: {
      type: String
    },
    ingredients: [{
      type: String
    }],
    allergens: [{
      type: String
    }],
    nutritionalInfo: {
      calories: Number,
      protein: Number,
      carbs: Number,
      fat: Number
    },
    isAvailable: {
      type: Boolean,
      default: true
    }
  },
  {
    timestamps: true
  }
);

export default mongoose.model<IFood>('Food', FoodSchema);
