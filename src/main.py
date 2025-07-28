from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from db.mongo import close_client
from routes import (
    authentication_router, employeeData_router, systemPermission_router, 
    projectData_router, taskData_router, timeTrackingData_router, analyticsData_router
)



allow_origins = [
    "http://localhost:3000",  
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------ startup ------ #
    print("--- Application Starting Up ---")
    yield
    # ------ shutdown ----- #
    print("--- Application Shutting Down ---")
    await close_client()

# Initialize the FastAPI application
app = FastAPI(
    title="Mercor Time Tracker API",
    description="API for the Insightful-like time tracking trial.",
    version="1.0.0",
    lifespan=lifespan  # Use the lifespan manager
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication_router, prefix="/api")
app.include_router(employeeData_router, prefix="/api")
app.include_router(systemPermission_router, prefix="/api")
app.include_router(projectData_router, prefix="/api")
app.include_router(taskData_router, prefix="/api")
app.include_router(timeTrackingData_router, prefix="/api")
app.include_router(analyticsData_router, prefix="/api")


@app.get("/healthz", tags=["Health Check"])
async def health_check():
    """
    A simple endpoint to confirm that the API is running.
    """
    return {"status": "ok", "message": "API is healthy"}


