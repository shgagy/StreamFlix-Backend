# StreamFlix - Movie & TV Series Streaming Platform

A full-stack streaming platform similar to Netflix, built with React frontend and Flask backend. Features include user authentication, content management, admin panel, ratings, comments, and more.

## 🚀 Live Demo

- **Frontend**: [Coming Soon]
- **Backend API**: [Coming Soon]
- **Admin Panel**: [Coming Soon]

## 📋 Features

### User Features
- **Authentication**: Register, login, password reset with JWT tokens
- **Content Browsing**: Browse movies and TV series with beautiful UI
- **Search & Filter**: Smart search with autocomplete and filtering by genre, year, rating
- **Content Details**: Comprehensive detail pages with cast, crew, ratings, and comments
- **User Interactions**: Rate content, add comments, maintain favorites list
- **Watch History**: Track viewing progress and history
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Optimized for desktop and mobile devices

### Admin Features
- **Dashboard**: Statistics and analytics overview
- **Content Management**: Add, edit, delete movies and series
- **User Management**: Manage user accounts and permissions
- **Episode Management**: Add episodes for TV series
- **Genre Management**: Create and manage content genres

### Technical Features
- **RESTful API**: Well-structured backend API with proper endpoints
- **Database**: SQLite with SQLAlchemy ORM
- **Security**: JWT authentication, password hashing, CORS support
- **File Upload**: Support for cover images and video files
- **Recommendation Engine**: Basic content recommendations
- **Responsive UI**: Mobile-first design with Tailwind CSS

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Vite** - Fast build tool and dev server

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-CORS** - Cross-origin resource sharing
- **PyJWT** - JSON Web Token implementation
- **Werkzeug** - Password hashing and security

### Database
- **SQLite** - Lightweight database for development
- **PostgreSQL** - Production database (configurable)

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or pnpm

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streaming-platform
   ```

2. **Set up Python virtual environment**
   ```bash
   cd streaming-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python seed_data.py
   ```

6. **Run the backend server**
   ```bash
   python src/main.py
   ```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd streaming-frontend
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   # or npm install
   ```

3. **Start development server**
   ```bash
   pnpm run dev
   # or npm run dev
   ```

The frontend will be available at `http://localhost:5174`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///streaming.db
JWT_SECRET_KEY=your-jwt-secret-here
CORS_ORIGINS=http://localhost:5174
```

#### Frontend
Update the API base URL in `src/lib/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### Get User Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>
```

### Content Endpoints

#### Get All Content
```http
GET /api/content?page=1&per_page=20&genre=action&year=2023
```

#### Get Content Details
```http
GET /api/content/{id}
```

#### Search Content
```http
GET /api/search?q=search_term
```

### User Interaction Endpoints

#### Rate Content
```http
POST /api/content/{id}/rating
Authorization: Bearer <token>
Content-Type: application/json

{
  "score": 5
}
```

#### Add Comment
```http
POST /api/content/{id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Great movie!",
  "parent_id": null
}
```

#### Add to Favorites
```http
POST /api/favorites
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": 1
}
```

### Admin Endpoints

#### Get Dashboard Stats
```http
GET /api/admin/stats
Authorization: Bearer <admin-token>
```

#### Manage Users
```http
GET /api/admin/users
POST /api/admin/users/{id}/toggle-status
Authorization: Bearer <admin-token>
```

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `password_hash` - Hashed password
- `is_admin` - Admin flag
- `is_active` - Account status
- `created_at` - Registration date

### Content Table
- `id` - Primary key
- `title` - Content title
- `description` - Content description
- `content_type` - 'movie' or 'series'
- `release_year` - Release year
- `duration` - Duration in minutes
- `rating` - Average rating
- `cover_image` - Cover image URL
- `video_url` - Video file URL
- `is_active` - Publication status

### Episodes Table
- `id` - Primary key
- `series_id` - Foreign key to content
- `season_number` - Season number
- `episode_number` - Episode number
- `title` - Episode title
- `description` - Episode description
- `duration` - Duration in minutes
- `video_url` - Video file URL

## 🎨 UI Components

The frontend uses a component-based architecture with reusable UI components:

- **Header** - Navigation and user menu
- **ContentCard** - Movie/series display cards
- **ContentDetail** - Detailed content view
- **AdminDashboard** - Admin panel interface
- **AuthForms** - Login and registration forms

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt password hashing
- **CORS Protection** - Configured cross-origin requests
- **Input Validation** - Server-side input validation
- **Admin Protection** - Admin-only route protection

## 🚀 Deployment

### Using Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

### Manual Deployment

#### Backend Deployment (DigitalOcean App Platform)
1. Create a new App on DigitalOcean App Platform.
2. Connect your GitHub repository.
3. Configure the build command (e.g., `pip install -r requirements.txt && python seed_data.py`) and run command (e.g., `gunicorn --bind 0.0.0.0:$PORT src.main:app`).
4. Set environment variables, including `DATABASE_URL` and `SECRET_KEY`.
5. Deploy the `streaming-backend` directory.

#### Frontend Deployment (Vercel/Netlify)
1. Build the frontend
   ```bash
   cd streaming-frontend
   pnpm run build
   ```
2. Deploy the `dist` folder to Vercel or Netlify
3. Update API base URL for production

## 🧪 Testing

### Demo Accounts

#### Admin Account
- **Username**: `admin`
- **Password**: `Admin123!`

#### Regular User Account
- **Username**: `john_doe`
- **Password**: `User123!`

### Sample Content
The application comes with pre-seeded content including:
- Movies: Pulp Fiction, The Shawshank Redemption, Inception
- TV Series: Stranger Things, Breaking Bad, The Crown

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- React team for the amazing framework
- Flask team for the lightweight Python framework
- Tailwind CSS for the utility-first CSS framework
- Lucide for the beautiful icons

## 📞 Support

For support, email support@streamflix.com or create an issue in the GitHub repository.

---

**Built with ❤️ by the StreamFlix Team**

