# FoodBeverages-CMS

A comprehensive Content Management System for managing food and beverage inventory, designed for restaurants, cafes, and food service businesses.

## Features

- 🍔 **Food Management**: Create, read, update, and delete food items with detailed information
- 📁 **Category Management**: Organize food items by categories
- 👥 **User Authentication**: Role-based access control (Admin, Manager, Staff)
- 🔒 **Secure API**: JWT-based authentication
- 📊 **Dashboard**: Overview of your food inventory
- 🌐 **RESTful API**: Clean and well-documented API endpoints
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

### Backend
- Node.js with Express
- TypeScript
- MongoDB with Mongoose
- JWT for authentication
- bcryptjs for password hashing

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API calls
- Modern CSS styling

## Prerequisites

- Node.js (v18 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/dadinjaenudin/FoodBeverages-CMS.git
cd FoodBeverages-CMS
```

2. Start the application with Docker Compose:
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Manual Installation

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Update the `.env` file with your configuration:
```
PORT=5000
MONGODB_URI=mongodb://localhost:27017/foodbeverages-cms
JWT_SECRET=your-secret-key-change-this-in-production
NODE_ENV=development
```

5. Start the backend server:
```bash
# Development mode
npm run dev

# Production mode
npm run build
npm start
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the frontend development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## API Endpoints

### Authentication
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Login user
- `GET /api/users` - Get all users (Admin only)

### Categories
- `GET /api/categories` - Get all categories
- `GET /api/categories/:id` - Get a specific category
- `POST /api/categories` - Create a new category (Admin/Manager)
- `PUT /api/categories/:id` - Update a category (Admin/Manager)
- `DELETE /api/categories/:id` - Delete a category (Admin)

### Foods
- `GET /api/foods` - Get all food items
- `GET /api/foods/:id` - Get a specific food item
- `POST /api/foods` - Create a new food item (Admin/Manager)
- `PUT /api/foods/:id` - Update a food item (Admin/Manager)
- `DELETE /api/foods/:id` - Delete a food item (Admin)

## User Roles

- **Admin**: Full access to all features including user management
- **Manager**: Can create, update, and view food items and categories
- **Staff**: Read-only access to food items and categories

## Testing

### Backend Tests
```bash
cd backend
npm test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Development

### Backend Development
```bash
cd backend
npm run dev
```

### Frontend Development
```bash
cd frontend
npm start
```

### Building for Production

#### Backend
```bash
cd backend
npm run build
npm start
```

#### Frontend
```bash
cd frontend
npm run build
```

## Project Structure

```
FoodBeverages-CMS/
├── backend/
│   ├── src/
│   │   ├── config/          # Configuration files
│   │   ├── controllers/     # Route controllers
│   │   ├── middleware/      # Custom middleware
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   └── index.ts         # Application entry point
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── App.tsx          # Main App component
│   │   └── index.tsx        # Application entry point
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
