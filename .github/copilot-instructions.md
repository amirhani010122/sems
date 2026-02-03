# Copilot / AI Agent instructions for SEMS 🤖

## Quick context
- SEMS is a backend-driven intelligent system for managing electricity consumption, energy plans, and AI-powered analysis.
- The architecture includes:
  - **Backend**: FastAPI (Python)
  - **Database**: MongoDB
  - **AI Modules**: Python (separate service)
  - **IoT Simulator**: Python script
  - **Authentication**: JWT

## Primary developer workflows 🔧

### Using Docker (Recommended):
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

### Manual Setup:
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

## Key files to reference 📁
- **Backend**:
  - Entry point: `backend/app/main.py`
  - Config: `backend/app/config.py`
  - Database: `backend/app/database.py`
  - API routes: `backend/app/api/`
  - Models: `backend/app/models/`
  - Schemas: `backend/app/schemas/`
  - Utilities: `backend/app/utils/`
- **AI Service**:
  - Entry point: `ai_service/main.py`
  - Services: `ai_service/services/`
- **IoT Simulator**:
  - Script: `iot_simulator/simulator.py`
- **Environment**:
  - Docker: `docker-compose.yml`
  - Python dependencies: `requirements.txt`
  - Environment variables: `.env.example`

## Project-specific conventions & important patterns ✅
- **Async-first stack**: FastAPI + `motor` (AsyncIOMotorClient). Prefer `async def` handlers and `await` DB calls.
- **JWT Authentication**: Tokens are created with `create_access_token` and validated via `get_current_user`.
- **Database**: MongoDB collections include `users`, `plans`, `devices`, `consumption`, and `alerts`. Convert ObjectIds to strings for API responses.
- **CORS**: Permissive (`allow_origins=['*']`) with custom middleware for private network clients.
- **AI Integration**: Backend proxies AI service calls via `/api/v1/ai` -> `settings.ai_service_url`.

## Integration & troubleshooting tips ⚠️
- **Database**: Ensure MongoDB is reachable at `MONGODB_URL`. Use `scripts/init_plans.py` to seed sample data.
- **AI Service**: If AI endpoints return 503, check `settings.ai_service_url` and AI service logs.
- **Authentication**: Debug traces for `get_current_user` are printed to the backend console for invalid tokens.
- **API Documentation**: Verify endpoints via Swagger UI at `http://localhost:8000/docs`.

---
If any section is unclear or you want me to expand examples (request bodies, sample cURL/HTTPX calls, or a short local dev script), tell me which parts to expand and I’ll update the file.