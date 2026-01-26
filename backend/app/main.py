from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_to_mongo, close_mongo_connection
from .api import auth, users, devices, consumption, plans, alerts, ai, internal

app = FastAPI(
    title="Smart Energy Management System",
    description="Backend API for SEMS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
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
