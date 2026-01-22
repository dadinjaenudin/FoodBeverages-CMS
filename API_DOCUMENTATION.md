# FoodBeverages CMS API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## User Endpoints

### Register a new user
```http
POST /users/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "staff"
}
```

**Response:**
```json
{
  "token": "jwt-token-here",
  "user": {
    "id": "user-id",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff"
  }
}
```

### Login
```http
POST /users/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "jwt-token-here",
  "user": {
    "id": "user-id",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff"
  }
}
```

### Get all users (Admin only)
```http
GET /users
```

**Response:**
```json
[
  {
    "id": "user-id",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff"
  }
]
```

## Category Endpoints

### Get all categories
```http
GET /categories
```

**Response:**
```json
[
  {
    "_id": "category-id",
    "name": "Beverages",
    "description": "All types of beverages",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "updatedAt": "2024-01-01T00:00:00.000Z"
  }
]
```

### Get a specific category
```http
GET /categories/:id
```

### Create a category (Admin/Manager only)
```http
POST /categories
```

**Request Body:**
```json
{
  "name": "Beverages",
  "description": "All types of beverages"
}
```

### Update a category (Admin/Manager only)
```http
PUT /categories/:id
```

**Request Body:**
```json
{
  "name": "Updated Category Name",
  "description": "Updated description"
}
```

### Delete a category (Admin only)
```http
DELETE /categories/:id
```

## Food Endpoints

### Get all food items
```http
GET /foods
```

**Response:**
```json
[
  {
    "_id": "food-id",
    "name": "Caesar Salad",
    "description": "Fresh romaine lettuce with Caesar dressing",
    "price": 12.99,
    "category": {
      "_id": "category-id",
      "name": "Salads"
    },
    "ingredients": ["lettuce", "parmesan", "croutons"],
    "allergens": ["dairy", "gluten"],
    "nutritionalInfo": {
      "calories": 350,
      "protein": 15,
      "carbs": 25,
      "fat": 20
    },
    "isAvailable": true,
    "createdAt": "2024-01-01T00:00:00.000Z",
    "updatedAt": "2024-01-01T00:00:00.000Z"
  }
]
```

### Get a specific food item
```http
GET /foods/:id
```

### Create a food item (Admin/Manager only)
```http
POST /foods
```

**Request Body:**
```json
{
  "name": "Caesar Salad",
  "description": "Fresh romaine lettuce with Caesar dressing",
  "price": 12.99,
  "category": "category-id",
  "ingredients": ["lettuce", "parmesan", "croutons"],
  "allergens": ["dairy", "gluten"],
  "nutritionalInfo": {
    "calories": 350,
    "protein": 15,
    "carbs": 25,
    "fat": 20
  },
  "isAvailable": true
}
```

### Update a food item (Admin/Manager only)
```http
PUT /foods/:id
```

**Request Body:**
```json
{
  "name": "Updated Food Name",
  "price": 15.99,
  "isAvailable": false
}
```

### Delete a food item (Admin only)
```http
DELETE /foods/:id
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Role-Based Access Control

- **Public**: Can view food items and categories
- **Staff**: Can view food items and categories
- **Manager**: Can create and update food items and categories
- **Admin**: Full access including delete operations and user management
