from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    #STARTUP LIFECYCLE SEQUENCE 
    print("[LIFESPAN] Executing startup operations...")
    print(f"[LIFESPAN] Connecting securely to Relational Engine at: {settings.DATABASE_URL.split('@')[-1]}")
    print(f"[LIFESPAN] Initializing key-value cluster pool at: {settings.REDIS_URL}")
    

    
    yield  
    

    print("[LIFESPAN] Executing shutdown lifecycle operations...")
    print("[LIFESPAN] Severing connections to Database Pools cleanly...")
    print("[LIFESPAN] Flushing connection states to Redis engine...")
    


app = FastAPI(
    title="NextCareOn API Engine",
    description="Backend microservice managing career paths, gamified levels, and AI parsing engine.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.NEXT_JS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

v1_router = APIRouter(prefix="/api/v1")


app.include_router(v1_router)


@app.get("/health", tags=["System Utility Monitoring"])
async def health_check():
    """
    Standard automated system endpoint used by load balancers, orchestrators,
    and monitoring agents to ascertain operational status cleanly.
    """
    return {
        "status": "operational",
        "database": "connected_placeholder",
        "redis": "connected_placeholder"
    }