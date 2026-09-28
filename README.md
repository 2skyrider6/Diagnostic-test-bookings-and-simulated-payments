# Diagnostic Test Booking Service

A backend service for diagnostic test bookings and simulated payments built with FastAPI and PostgreSQL.

## Features

- User authentication with JWT
- Diagnostic centres and tests management
- Booking system with status tracking
- Simulated payment processing
- Idempotent payment webhook
- Error handling and edge case management

## Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional, for caching)
- Docker and Docker Compose (for containerized deployment)

## Getting Started

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
7. Access the API at `http://localhost:8000`

### Docker Deployment

1. Build and start the services:
   ```bash
   docker-compose up --build
   ```
2. The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Authentication

All endpoints except authentication require a JWT token obtained from:
- POST `/api/v1/auth/login` - Returns access token
- POST `/api/v1/auth/signup` - Register new user

Include the token in the Authorization header: `Authorization: Bearer <token>`

### Endpoints

#### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Diagnostic Centres
- `POST /api/v1/centres-tests/centres/` - Create a new centre
- `GET /api/v1/centres-tests/centres/` - List all centres
- `GET /api/v1/centres-tests/centres/{centre_id}` - Get centre by ID

#### Diagnostic Tests
- `POST /api/v1/centres-tests/tests/` - Create a new test
- `GET /api/v1/centres-tests/tests/` - List all tests (optionally filter by centre)
- `GET /api/v1/centres-tests/tests/{test_id}` - Get test by ID

#### Bookings
- `POST /api/v1/bookings/` - Create a new booking
- `GET /api/v1/bookings/` - List user's bookings
- `GET /api/v1/bookings/{booking_id}` - Get booking by ID
- `PUT /api/v1/bookings/{booking_id}` - Update booking (pending only)
- `DELETE /api/v1/bookings/{booking_id}` - Cancel booking

#### Payments
- `POST /api/v1/payments/` - Process payment for a booking
- `POST /api/v1/payments/webhook/` - Payment webhook (idempotent)
- `GET /api/v1/payments/{payment_id}` - Get payment details

## Database Schema

### Users
- id (PK)
- email (unique)
- hashed_password
- full_name
- role (patient/admin)
- is_active
- created_at
- updated_at

### Diagnostic Centres
- id (PK)
- name
- location
- created_at
- updated_at

### Diagnostic Tests
- id (PK)
- name
- price
- centre_id (FK)
- created_at
- updated_at

### Bookings
- id (PK)
- user_id (FK)
- test_id (FK)
- centre_id (FK)
- appointment_datetime
- amount
- status (pending/confirmed/failed/cancelled)
- created_at
- updated_at

### Payments
- id (PK)
- booking_id (FK, unique)
- user_id (FK)
- amount
- status (pending/success/failed)
- transaction_id (unique)
- created_at
- updated_at

## Assumptions

1. Users can only book tests for themselves (no admin booking for others in this version)
2. Payment simulation uses a 70% success rate for demonstration
3. Appointment times must be in the future
4. Only pending bookings can be updated or cancelled
5. Webhook endpoint is idempotent to prevent duplicate processing
6. Transaction IDs are generated as UUIDs for uniqueness
7. All monetary values use DECIMAL(10,2) for precision

## Potential Improvements

With more time, I would implement:

1. **Role-based access control**: Admin users could manage centres/tests
2. **Email notifications**: Send booking confirmations and reminders
3. **Advanced filtering**: Search centres by location, tests by name/price range
4. **Rate limiting**: Prevent API abuse
5. **Caching**: Use Redis for frequently accessed data
6. **Background jobs**: Use Celery for payment processing and notifications
7. **Comprehensive testing**: Increase test coverage with edge cases
8. **Logging**: Structured logging with log levels and rotation
9. **Input validation**: More robust validation for business rules
10. **API versioning**: Better versioning strategy for future changes
11. **Database migrations**: Using Alembic for schema changes
12. **Security enhancements**: Password reset, 2FA, account locking
13. **Monitoring**: Health checks, metrics, and tracing
14. **Internationalization**: Support for multiple languages and currencies
15. **Payment provider integration**: Replace simulation with real payment gateway

## Testing

Run tests with:
```bash
pytest
```

## License

This project is licensed under the MIT License.