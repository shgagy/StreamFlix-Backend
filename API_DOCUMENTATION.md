# StreamFlix API Documentation

This document provides comprehensive documentation for the StreamFlix API endpoints.

## Base URL
```
http://localhost:5001/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Authentication Endpoints

### Register User
Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "string (required, 3-50 characters)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 characters)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "is_admin": false,
      "created_at": "2025-01-01T00:00:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "User registered successfully"
}
```

### Login User
Authenticate a user and receive a JWT token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "is_admin": false
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Login successful"
}
```

### Get User Profile
Get the current user's profile information.

**Endpoint:** `GET /auth/profile`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "is_admin": false,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Update User Profile
Update the current user's profile information.

**Endpoint:** `PUT /auth/profile`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "string (optional)",
  "current_password": "string (required if changing password)",
  "new_password": "string (optional)"
}
```

## Content Endpoints

### Get All Content
Retrieve a list of movies and TV series with pagination and filtering.

**Endpoint:** `GET /content`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20, max: 100) - Items per page
- `content_type` (string) - Filter by 'movie' or 'series'
- `genre` (string) - Filter by genre name
- `year` (integer) - Filter by release year
- `sort_by` (string) - Sort by 'title', 'release_year', 'rating', 'view_count'
- `order` (string) - 'asc' or 'desc'
- `search` (string) - Search in title and description

**Example:** `GET /content?page=1&per_page=10&content_type=movie&genre=action&sort_by=rating&order=desc`

**Response:**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "title": "Inception",
        "description": "A thief who steals corporate secrets...",
        "content_type": "movie",
        "release_year": 2010,
        "duration": 148,
        "rating": 8.8,
        "imdb_rating": 8.8,
        "cover_image": "https://example.com/inception.jpg",
        "genres": [
          {"id": 1, "name": "Action"},
          {"id": 2, "name": "Sci-Fi"}
        ],
        "view_count": 1250,
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 50,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Get Content Details
Get detailed information about a specific movie or TV series.

**Endpoint:** `GET /content/{id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Inception",
    "description": "A thief who steals corporate secrets through dream-sharing technology...",
    "content_type": "movie",
    "release_year": 2010,
    "duration": 148,
    "rating": 8.8,
    "imdb_rating": 8.8,
    "cover_image": "https://example.com/inception.jpg",
    "video_url": "https://example.com/inception.mp4",
    "director": "Christopher Nolan",
    "cast": "Leonardo DiCaprio, Marion Cotillard, Tom Hardy",
    "country": "USA",
    "language": "English",
    "genres": [
      {"id": 1, "name": "Action"},
      {"id": 2, "name": "Sci-Fi"}
    ],
    "view_count": 1250,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

### Search Content
Search for content by title, description, or other fields.

**Endpoint:** `GET /search`

**Query Parameters:**
- `q` (string, required) - Search query
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20) - Items per page

**Example:** `GET /search?q=inception&page=1&per_page=10`

**Response:** Same format as Get All Content

### Get Content Recommendations
Get personalized content recommendations for the authenticated user.

**Endpoint:** `GET /recommendations`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (integer, default: 10) - Number of recommendations

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": 1,
        "title": "Inception",
        "content_type": "movie",
        "rating": 8.8,
        "cover_image": "https://example.com/inception.jpg",
        "reason": "Based on your interest in Sci-Fi movies"
      }
    ]
  }
}
```

## User Interaction Endpoints

### Rate Content
Rate a movie or TV series.

**Endpoint:** `POST /content/{id}/rating`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "score": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rating": {
      "id": 1,
      "user_id": 1,
      "content_id": 1,
      "score": 5,
      "created_at": "2025-01-01T00:00:00Z"
    },
    "average_rating": 8.8
  },
  "message": "Rating submitted successfully"
}
```

### Get User Rating
Get the current user's rating for specific content.

**Endpoint:** `GET /content/{id}/rating`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "score": 5,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Add Comment
Add a comment to a movie or TV series.

**Endpoint:** `POST /content/{id}/comments`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "text": "Great movie! Highly recommended.",
  "parent_id": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "comment": {
      "id": 1,
      "user_id": 1,
      "content_id": 1,
      "text": "Great movie! Highly recommended.",
      "parent_id": null,
      "created_at": "2025-01-01T00:00:00Z",
      "user": {
        "id": 1,
        "username": "john_doe"
      }
    }
  },
  "message": "Comment added successfully"
}
```

### Get Comments
Get comments for specific content.

**Endpoint:** `GET /content/{id}/comments`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20) - Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 1,
        "user_id": 1,
        "content_id": 1,
        "text": "Great movie! Highly recommended.",
        "parent_id": null,
        "created_at": "2025-01-01T00:00:00Z",
        "user": {
          "id": 1,
          "username": "john_doe"
        },
        "replies": []
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

### Add to Favorites
Add content to user's favorites list.

**Endpoint:** `POST /favorites`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "favorite": {
      "id": 1,
      "user_id": 1,
      "content_id": 1,
      "created_at": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Added to favorites"
}
```

### Remove from Favorites
Remove content from user's favorites list.

**Endpoint:** `DELETE /favorites/{content_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Removed from favorites"
}
```

### Get Favorites
Get user's favorites list.

**Endpoint:** `GET /favorites`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20) - Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "id": 1,
        "content": {
          "id": 1,
          "title": "Inception",
          "content_type": "movie",
          "cover_image": "https://example.com/inception.jpg",
          "rating": 8.8
        },
        "created_at": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 3,
      "pages": 1
    }
  }
}
```

### Update Watch History
Update user's watch history and progress.

**Endpoint:** `POST /watch-history`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content_id": 1,
  "episode_id": null,
  "progress": 45.5,
  "completed": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "watch_history": {
      "id": 1,
      "user_id": 1,
      "content_id": 1,
      "episode_id": null,
      "progress": 45.5,
      "completed": false,
      "last_watched": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Watch history updated"
}
```

### Get Watch History
Get user's watch history.

**Endpoint:** `GET /watch-history`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20) - Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "watch_history": [
      {
        "id": 1,
        "content": {
          "id": 1,
          "title": "Inception",
          "content_type": "movie",
          "cover_image": "https://example.com/inception.jpg"
        },
        "progress": 45.5,
        "completed": false,
        "last_watched": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 10,
      "pages": 1
    }
  }
}
```

## Admin Endpoints

All admin endpoints require authentication with an admin user account.

### Get Admin Statistics
Get platform statistics for the admin dashboard.

**Endpoint:** `GET /admin/stats`

**Headers:** `Authorization: Bearer <admin-token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1247,
    "total_content": 156,
    "total_views": 45892,
    "active_users": 89,
    "content_by_genre": [
      {"name": "Action", "count": 25},
      {"name": "Drama", "count": 30},
      {"name": "Comedy", "count": 20}
    ],
    "top_content": [
      {
        "id": 1,
        "title": "Inception",
        "view_count": 1250,
        "rating": 8.8
      }
    ]
  }
}
```

### Get All Users (Admin)
Get a list of all users with admin privileges.

**Endpoint:** `GET /admin/users`

**Headers:** `Authorization: Bearer <admin-token>`

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `per_page` (integer, default: 20) - Items per page
- `search` (string) - Search by username or email
- `is_active` (boolean) - Filter by active status

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "is_admin": false,
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-02T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1247,
      "pages": 63
    }
  }
}
```

### Toggle User Status (Admin)
Activate or deactivate a user account.

**Endpoint:** `POST /admin/users/{user_id}/toggle-status`

**Headers:** `Authorization: Bearer <admin-token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "is_active": false
    }
  },
  "message": "User status updated"
}
```

### Create Content (Admin)
Create new movie or TV series content.

**Endpoint:** `POST /content`

**Headers:** `Authorization: Bearer <admin-token>`

**Request Body:**
```json
{
  "title": "string (required)",
  "description": "string (required)",
  "content_type": "movie|series (required)",
  "release_year": 2023,
  "duration": 120,
  "cover_image": "string (URL)",
  "video_url": "string (URL)",
  "director": "string",
  "cast": "string",
  "country": "string",
  "language": "string",
  "imdb_rating": 8.5,
  "genre_ids": [1, 2, 3]
}
```

### Update Content (Admin)
Update existing content.

**Endpoint:** `PUT /content/{id}`

**Headers:** `Authorization: Bearer <admin-token>`

**Request Body:** Same as Create Content

### Delete Content (Admin)
Delete content (soft delete - sets is_active to false).

**Endpoint:** `DELETE /content/{id}`

**Headers:** `Authorization: Bearer <admin-token>`

**Response:**
```json
{
  "success": true,
  "message": "Content deleted successfully"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_REQUIRED` | Authentication token required |
| `INVALID_CREDENTIALS` | Invalid username or password |
| `ACCESS_DENIED` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `DUPLICATE_ENTRY` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **General endpoints**: 100 requests per minute per IP
- **Authentication endpoints**: 10 requests per minute per IP
- **Admin endpoints**: 200 requests per minute per authenticated admin

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination with the following parameters:

- `page` (integer, default: 1) - Page number (1-based)
- `per_page` (integer, default: 20, max: 100) - Items per page

Pagination information is included in the response:
```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Content Types

The API supports the following content types:

- **Request**: `application/json`
- **Response**: `application/json`
- **File Upload**: `multipart/form-data`

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for the following origins:
- `http://localhost:3000` (Production frontend)
- `http://localhost:5174` (Development frontend)

## Webhooks (Future Feature)

The API will support webhooks for real-time notifications:

- New content added
- User registration
- Content rating changes
- Comment notifications

---

For more information or support, please contact the development team or create an issue in the GitHub repository.

