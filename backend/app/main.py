from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_to_mongo, close_mongo_connection, get_database
from .api import auth, users, devices, consumption, plans, alerts, ai, internal

app = FastAPI(
    title="Smart Energy Management System",
    description="Backend API for SEMS",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Response

# 1. الـ CORS Middleware الأساسي
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# 2. الـ Middleware السحري للـ Web (عشان يوافق على الـ Private Network والـ OPTIONS)
@app.middleware("http")
async def cors_and_private_network_fix(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

    # Start background task to mark stale devices as inactive
    import asyncio
    from datetime import datetime, timedelta
    from .config import settings

    async def device_status_worker():
        db = get_database()
        interval = settings.device_status_interval_seconds
        timeout = settings.device_timeout_seconds
        while True:
            try:
                cutoff = datetime.utcnow() - timedelta(seconds=timeout)
                result = await db.devices.update_many(
                    {"last_seen": {"$lt": cutoff}, "is_active": True},
                    {"$set": {"is_active": False}}
                )
                if getattr(result, "modified_count", 0):
                    print(f"Device status worker: set {result.modified_count} devices to inactive (last_seen < {cutoff.isoformat()})")
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Device status worker error: {e}")
                await asyncio.sleep(interval)

    app.state.device_status_task = asyncio.create_task(device_status_worker())


@app.on_event("shutdown")
async def shutdown_event():
    # Cancel background task if running
    import asyncio
    task = getattr(app.state, "device_status_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await close_mongo_connection()


@app.get("/")
async def root():
    return {"message": "Smart Energy Management System API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(consumption.router, prefix="/api/v1/consumption", tags=["Consumption"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["Plans"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(internal.router, prefix="/api/internal", tags=["Internal"])
