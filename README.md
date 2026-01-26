# Smart Energy Management System (SEMS)

A backend-driven intelligent system for managing electricity consumption, energy plans, and AI-powered analysis.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI Modules**: Python (separate service)
- **IoT Simulator**: Python script
- **Authentication**: JWT

## Project Structure

```
sems/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── utils/
│   └── requirements.txt
├── ai_service/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   └── services/
├── iot_simulator/
│   ├── __init__.py
│   └── simulator.py
└── docker-compose.yml
```

## Setup

### Option 1: Using Docker (Recommended)

1. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

2. Start all services:
```bash
docker-compose up -d
```

3. Initialize sample plans:
```bash
python scripts/init_plans.py
```

4. Run the IoT simulator (in a separate terminal):
```bash
python iot_simulator/simulator.py
```

### Option 2: Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Start MongoDB (if not using Docker):
```bash
# MongoDB must be running on localhost:27017
# Or use: docker run -d -p 27017:27017 mongo:7.0
```

4. Initialize sample plans:
```bash
python scripts/init_plans.py
```

5. Start the backend (Terminal 1):
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Start the AI service (Terminal 2):
```bash
python -m ai_service.main
```

7. Run the IoT simulator (Terminal 3):
```bash
python iot_simulator/simulator.py
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for required configuration.
