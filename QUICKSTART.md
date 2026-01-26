# Quick Start Guide

## Prerequisites

- Python 3.11+
- MongoDB (or use Docker)
- pip

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (defaults should work for local development)
```

### 3. Start MongoDB

**Option A: Using Docker**
```bash
docker run -d -p 27017:27017 --name sems_mongodb mongo:7.0
```

**Option B: Local MongoDB**
```bash
# Ensure MongoDB is running on localhost:27017
```

### 4. Initialize Sample Plans

```bash
python scripts/init_plans.py
```

This creates 4 sample energy plans:
- Basic Plan: 100 kWh / 30 days
- Standard Plan: 250 kWh / 30 days
- Premium Plan: 500 kWh / 30 days
- Weekly Plan: 50 kWh / 7 days

### 5. Start Backend Service

```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 6. Start AI Service

```bash
# Terminal 2
python -m ai_service.main
```

AI Service will be available at: http://localhost:8001

### 7. Run IoT Simulator

```bash
# Terminal 3
python iot_simulator/simulator.py
```

The simulator will:
- Register a test user (if not exists)
- Register a device
- Send consumption data every 60 seconds

## Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 3. Register a Device

```bash
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "my_device_001",
    "device_name": "My Smart Meter"
  }'
```

### 4. Subscribe to a Plan

First, get available plans:
```bash
curl "http://localhost:8000/api/v1/plans/available"
```

Then subscribe (use a plan ID from the response):
```bash
curl -X POST "http://localhost:8000/api/v1/plans/subscribe" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "PLAN_ID_HERE"
  }'
```

### 5. Send Consumption Data

```bash
curl -X POST "http://localhost:8000/api/v1/consumption" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "my_device_001",
    "consumption_value": 1.5
  }'
```

### 6. Get AI Analysis

```bash
curl "http://localhost:8000/api/v1/ai/analysis" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Get Alerts

```bash
curl "http://localhost:8000/api/v1/alerts" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Using Docker Compose

For a complete setup with Docker:

```bash
# Start all services
docker-compose up -d

# Initialize plans
python scripts/init_plans.py

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## API Endpoints Summary

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Users
- `GET /api/v1/users/me` - Get current user info

### Devices
- `POST /api/v1/devices` - Register device
- `GET /api/v1/devices` - List user devices
- `GET /api/v1/devices/{device_id}` - Get device details

### Consumption
- `POST /api/v1/consumption` - Record consumption
- `GET /api/v1/consumption` - Get consumption history

### Plans
- `GET /api/v1/plans/available` - List available plans
- `POST /api/v1/plans/subscribe` - Subscribe to plan
- `GET /api/v1/plans/subscription` - Get current subscription

### Alerts
- `GET /api/v1/alerts` - Get user alerts

### AI
- `GET /api/v1/ai/analysis` - Get consumption analysis
- `GET /api/v1/ai/prediction` - Get consumption prediction
- `GET /api/v1/ai/plan-exhaustion` - Predict plan exhaustion date
- `GET /api/v1/ai/recommendations` - Get energy-saving recommendations

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `docker ps` or check MongoDB service
- Verify connection string in `.env`: `MONGODB_URL=mongodb://localhost:27017`

### Port Already in Use
- Change ports in `.env` file
- Or stop the service using the port

### AI Service Unavailable
- Ensure AI service is running on port 8001
- Check `AI_SERVICE_URL` in backend `.env`

### No Plans Available
- Run `python scripts/init_plans.py` to create sample plans
