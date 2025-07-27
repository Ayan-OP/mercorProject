from contextlib import asynccontextmanager
from fastapi import FastAPI
#from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from db.mongo import close_client
from routes import authentication_router, employeeData_router, systemPermission_router, projectData_router
#from utils.http_client import aclose_httpx_client
#from utils.token_manager import AsyncGoogleTokenManager


# allow_origins = [origin.strip() for origin in settings.CORS_ORIGIN_LIST.split(",") if origin.strip()]
# allow_credentials = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------ startup ------ #
    # await init_indexes()
    
    # 1) create one manager for the whole app
    # app.state.token_mgr = AsyncGoogleTokenManager()
    # # 2) (optional) fetch first token so the first real request doesn't block
    # await app.state.token_mgr.get_access_token()
    print("--- Application Starting Up ---")
    yield
    # ------ shutdown ----- #
    print("--- Application Shutting Down ---")
    await close_client()
    #await aclose_httpx_client()

# Initialize the FastAPI application
app = FastAPI(
    title="T3 Time Tracker API",
    description="API for the Insightful-like time tracking trial.",
    version="1.0.0",
    lifespan=lifespan  # Use the lifespan manager
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allow_origins,  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(authentication_router, prefix="/api")
app.include_router(employeeData_router, prefix="/api")
app.include_router(systemPermission_router, prefix="/api")
app.include_router(projectData_router, prefix="/api")
# app.include_router(ads_router, prefix="/ingest", tags=["ingest"])
# app.include_router(winning_creative_router, prefix="/metrics", tags=["Performance Metrics"])
# app.include_router(insights_router, prefix="/insights", tags=["Insights"])
# app.include_router(s3_resource_router, prefix="/resource", tags=["S3 Resources"])
# app.include_router(budgeting_router, prefix="/budget", tags=["Budgeting"])
# app.include_router(google_budgeting_router, prefix="/google/budget", tags=["Budgeting"])
# app.include_router(google_insights_router, prefix="/google/insights", tags=["Google Insights"])
# app.include_router(comparative_analysis_router, prefix="/metrics", tags=["Performance Metrics"])
# app.include_router(creative_deep_dive_router, prefix="/metrics", tags=["Performance Metrics"])
# app.include_router(ai_reporting_router, prefix="/ai-reporting", tags=["AI Reporting"])
# app.include_router(winning_creative_google_router, prefix="/google/metrics", tags=["Performance Metrics"])
# app.include_router(google_comparative_analysis_router, prefix="/google/metrics", tags=["Performance Metrics"])
# app.include_router(google_creative_deep_dive_router, prefix="/google/metrics", tags=["Performance Metrics"])
# app.include_router(tagging_router, prefix="/tagging", tags=["Tagging"])


@app.get("/healthz", tags=["Health Check"])
async def health_check():
    """
    A simple endpoint to confirm that the API is running.
    """
    return {"status": "ok", "message": "API is healthy"}


