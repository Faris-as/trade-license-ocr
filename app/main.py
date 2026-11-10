"""
FastAPI Application - Trade License OCR System
This is the main entry point for the API.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from app.api.routes import router as ocr_router


# ============================================================================
# LIFESPAN - startup/shutdown context (replaces deprecated on_event hooks)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once at startup and once at shutdown.

    Startup: loads the YOLO model (so the first request isn't slow).
    Shutdown: reserved for closing connections / resource cleanup.
    """
    print("=" * 60)
    print("🚀 Trade License OCR API Starting...")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"📚 Swagger UI: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print("=" * 60)

    print("\n🔧 Initializing OCR services...")
    try:
        from app.services.ocr_service import load_model
        load_model()
        print("✅ OCR model loaded successfully\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not pre-load model: {str(e)}\n")

    yield

    print("\n" + "=" * 60)
    print("🛑 Trade License OCR API Shutting Down...")
    print(f"📅 Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Trade License OCR API",
    description="Extract structured data from Abu Dhabi Trade Licenses using AI-powered OCR",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI location
    redoc_url="/redoc",    # Alternative documentation
    lifespan=lifespan,
)

# ============================================================================
# CORS MIDDLEWARE - Allows frontend to call this API
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    # shortcut: wildcard origins with no deploy target yet; credentials are
    # off (no cookies/schema auth), which drops the invalid insecure combo.
    # Ceiling: fine for LAN/open API. Upgrade path: set CORS_ORIGINS to the
    # real frontend domain with regex when auth lands.
    allow_origins=["*"],  # In production, specify exact domains
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Include OCR routes
app.include_router(ocr_router)


# ============================================================================
# ROOT ENDPOINT - Welcome message
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Returns welcome message and API info.
    """
    return {
        "message": "Welcome to Trade License OCR API",
        "version": "1.0.0",
        "docs": "Visit /docs for Swagger documentation",
        "endpoints": {
            "ocr": "/ocr/trade-license",
            "health": "/health",
            "ocr_health": "/ocr/health"
        },
        "status": "running"
    }


# ============================================================================
# HEALTH ENDPOINT - Check if server is alive
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Trade License OCR API",
        "version": "1.0.0"
    }
