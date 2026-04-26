# SERVEX PRO - Smart Local Service Marketplace

A comprehensive web-based service marketplace platform with real-time matching, dynamic pricing, and provider bidding system.

## Project Overview

SERVEX PRO connects customers with verified service providers (plumbers, electricians, tutors, mechanics, cleaners, etc.) using intelligent matching algorithms, dynamic pricing, and real-time booking systems.

## Features

### Core Features
- **User & Provider Registration/Login** - Secure authentication with JWT tokens
- **Service Listing** - Browse available services (plumber, electrician, tutor, etc.)
- **Booking System** - Create and manage service bookings
- **Provider Availability** - Real-time availability tracking
- **Booking History** - View past bookings and history
- **Rating System** - Rate and review service providers

### Advanced Features
- **Smart Matching Algorithm** - Score = (0.4 × Rating) − (0.3 × Distance) − (0.3 × Price)
- **Dynamic Pricing Engine** - Price = Base Price × (Demand / Supply)
- **Provider Bidding System** - Multiple providers can bid on jobs
- **Real-Time Updates** - WebSocket-based real-time communication
- **Location Tracking** - Geolocation support for distance calculation

## Technology Stack

### Backend
- **Framework**: Flask
- **Real-Time**: Flask-SocketIO (WebSockets)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt

### Frontend
- **HTML5, CSS3, JavaScript**
- **Socket.IO Client** - Real-time communication
- **Geolocation API** - Location services

### APIs
- **Google Maps API** - Location & tracking (for future implementation)

## Project Structure

```
servex-pro/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── models.py          # Database models
│   │   ├── routes/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── user.py            # User endpoints
│   │   │   ├── provider.py        # Provider endpoints
│   │   │   ├── booking.py         # Booking endpoints
│   │   │   ├── matching.py        # Matching & bidding endpoints
│   │   │   ├── pricing.py         # Pricing endpoints
│   │   │   └── rating.py          # Rating endpoints
│   │   ├── utils/
│   │   │   ├── auth.py            # JWT utilities
│   │   │   ├── matching.py        # Matching algorithm
│   │   │   └── pricing.py         # Pricing engine
│   │   ├── events.py              # SocketIO events
│   │   └── __init__.py            # Flask app factory
│   ├── config.py                  # Configuration
│   ├── run.py                     # Application entry point
│   ├── requirements.txt           # Python dependencies
│   └── .env.example              # Environment variables template
│
├── frontend/
│   ├── index.html                # Home page
│   ├── login.html                # Login page
│   ├── register.html             # Registration page
│   ├── dashboard.html            # User dashboard
│   ├── css/
│   │   └── style.css             # Styling
│   ├── js/
│   │   ├── main.js               # Main utilities
│   │   ├── auth.js               # Authentication logic
│   │   └── dashboard.js          # Dashboard logic
│   └── assets/                   # Static assets
│
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- Node.js (for package management, optional)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Ensure MongoDB is running**
   ```bash
   # If local MongoDB
   mongod
   
   # Or use MongoDB Atlas - update MONGO_URI in .env
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The backend server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Start a local server** (Python)
   ```bash
   python -m http.server 8000
   ```

   Or use any other local server (Node.js http-server, etc.)

3. **Access the application**
   Open `http://localhost:8000` in your browser

## API Endpoints

### Authentication
- `POST /api/auth/register/customer` - Register customer
- `POST /api/auth/register/provider` - Register provider
- `POST /api/auth/login/customer` - Login as customer
- `POST /api/auth/login/provider` - Login as provider

### Users
- `GET /api/users/<user_id>` - Get user profile
- `PUT /api/users/<user_id>` - Update user profile
- `GET /api/users/<user_id>/bookings` - Get user bookings
- `GET /api/users/<user_id>/ratings` - Get user ratings

### Providers
- `GET /api/providers/<provider_id>` - Get provider profile
- `PUT /api/providers/<provider_id>` - Update provider profile
- `PUT /api/providers/<provider_id>/availability` - Update availability
- `GET /api/providers/<provider_id>/jobs` - Get provider jobs
- `GET /api/providers/by-service/<service_type>` - Get providers by service

### Bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/<booking_id>` - Get booking details
- `PUT /api/bookings/<booking_id>/status` - Update booking status
- `POST /api/bookings/<booking_id>/cancel` - Cancel booking

### Matching & Bidding
- `POST /api/matching/find-providers/<service_type>` - Find providers
- `POST /api/matching/bid/<booking_id>` - Place bid
- `GET /api/matching/bids/<booking_id>` - Get booking bids
- `POST /api/matching/select-provider/<booking_id>/<bid_id>` - Select provider

### Pricing
- `POST /api/pricing/calculate` - Calculate dynamic price
- `GET /api/pricing/metrics/<service_type>` - Get pricing metrics

### Ratings
- `POST /api/ratings` - Create rating
- `GET /api/ratings/<user_id>` - Get user ratings

## Real-Time Events (WebSocket)

### Client -> Server
- `connect` - Establish connection
- `booking_update` - Broadcast booking status
- `provider_location_update` - Update provider location
- `join_booking_room` - Join booking-specific room
- `leave_booking_room` - Leave booking room
- `broadcast_to_booking` - Send message to booking room

### Server -> Client
- `booking_status_changed` - Booking status update
- `provider_location_updated` - Provider location update
- `notification` - General notification
- `booking_message` - Message in booking room

## Algorithmic Components

### Matching Algorithm
```
Score = (0.4 × Rating) − (0.3 × Distance) − (0.3 × Price)

Where:
- Rating: Normalized to 0-1 scale (max rating = 5)
- Distance: Normalized to 0-1 scale (max distance = 50km)
- Price: Normalized to 0-1 scale (max price = 200 units)
```

### Dynamic Pricing
```
Price = Base Price × (Demand / Supply)

Where:
- Demand Score: Based on recent bookings (0-1)
- Supply Score: Based on available providers (0-1)
- Multiplier Range: 0.5x - 2.0x
```

## Database Schema

### Users Collection
```javascript
{
    _id: ObjectId,
    name: String,
    email: String (unique),
    password: String (hashed),
    phone: String,
    location: {
        latitude: Number,
        longitude: Number,
        address: String
    },
    role: String ("customer"),
    rating: Number,
    total_bookings: Number,
    created_at: Date,
    updated_at: Date,
    is_active: Boolean
}
```

### Providers Collection
```javascript
{
    _id: ObjectId,
    name: String,
    email: String (unique),
    password: String (hashed),
    phone: String,
    service_type: String,
    location: {
        latitude: Number,
        longitude: Number,
        address: String
    },
    experience_years: Number,
    hourly_rate: Number,
    rating: Number,
    total_jobs: Number,
    available: Boolean,
    is_verified: Boolean,
    created_at: Date,
    updated_at: Date,
    is_active: Boolean
}
```

### Bookings Collection
```javascript
{
    _id: ObjectId,
    user_id: ObjectId (ref: users),
    service_type: String,
    description: String,
    location: Object,
    scheduled_date: Date,
    estimated_hours: Number,
    provider_id: ObjectId (ref: providers),
    status: String ("pending", "accepted", "in_progress", "completed", "cancelled"),
    base_price: Number,
    final_price: Number,
    bids: [ObjectId],
    created_at: Date,
    updated_at: Date,
    completed_at: Date
}
```

## Configuration

Edit `.env` file to configure:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/servex_pro
JWT_SECRET=your-jwt-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

## Usage Example

### As a Customer:
1. Register an account
2. Search for a service (e.g., "Plumber")
3. Create a booking with details
4. View bids from providers
5. Select the best provider
6. Track service in real-time
7. Rate the provider after completion

### As a Provider:
1. Register as a service provider
2. Set availability and hourly rate
3. Receive notifications for matching bookings
4. Place bids on jobs
5. Accept bookings and complete services
6. Build ratings and reviews

## Future Enhancements

- Live location tracking with Google Maps integration
- In-app chat system between users and providers
- AI-based price prediction
- Admin analytics dashboard
- Payment gateway integration
- Mobile app (React Native/Flutter)
- Provider verification and certifications
- Advanced filtering and search
- Subscription plans
- Commission and revenue management

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Real-time communication | Flask-SocketIO with WebSockets |
| Complex matching logic | Weighted scoring algorithm |
| Scalability | MongoDB scalability, async operations |
| Data security | JWT, bcrypt hashing, CORS |

## Project Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 1 Week | Setup & Authentication |
| Phase 2 | 1 Week | Provider & Booking System |
| Phase 3 | 1 Week | Matching & Pricing Engine |
| Phase 4 | 1 Week | Real-Time Features |
| Phase 5 | 1 Week | Testing & Deployment |

## Testing

### Manual Testing
1. Test user registration and login
2. Create bookings and view them
3. Place and receive bids
4. Update booking status
5. Test real-time updates
6. Rate service providers

### Automated Testing (Future)
- Unit tests for models
- Integration tests for API endpoints
- Load testing for real-time features

## Deployment

### For Production:
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Enable HTTPS/SSL
4. Use MongoDB Atlas
5. Set secure environment variables
6. Deploy frontend to CDN (Netlify, Vercel, etc.)
7. Deploy backend to cloud (Heroku, AWS, etc.)

## Contributors

- Backend Developer – API, database, logic
- Frontend Developer – UI/UX, integration

## License

This project is designed as an educational and commercial demonstration of full-stack web development with modern technologies.

## Support

For issues, questions, or contributions, please open an issue or contact the development team.

---

**SERVEX PRO** - Making local services accessible, transparent, and efficient.
