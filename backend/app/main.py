import os
import time
import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.database import Base, engine, SessionLocal
from .routers import auth, documents, verify, analytics, chat, export
from .seed.seed_data import seed_database

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bizlens.api")

# Auto-create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BizLens AI — Core API Server",
    description="Deterministic Document Intelligence + Polygon Amoy Proof-of-Document Notarization Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware allowing web3 dApps and local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID & Latency Middleware
@app.middleware("http")
async def add_process_time_and_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{process_time:.2f}"
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[Req {req_id}] Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error occurred. Please verify document format or retry.",
            "request_id": req_id
        }
    )


# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(verify.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(export.router, prefix="/api")


# Health Check
@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint verifying Gemini model and Polygon network targets."""
    return {
        "status": "ok",
        "service": "BizLens AI",
        "gemini_model": settings.GEMINI_MODEL,
        "blockchain_network": "Polygon Amoy Testnet",
        "chain_id": settings.CHAIN_ID,
        "contract_address": settings.CONTRACT_ADDRESS
    }


# Auto-seed sample Indian SMB documents on startup if DB is fresh
@app.on_event("startup")
def startup_event():
    logger.info("Initializing BizLens AI engine and verifying database tables...")
    try:
        db = SessionLocal()
        seed_database(db)
        db.close()
    except Exception as e:
        logger.warning(f"Startup seed notice: {e}")


# Serve static frontend if directory exists
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def serve_index():
        idx_file = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(idx_file):
            with open(idx_file, "r", encoding="utf-8") as f:
                return f.read()
        return "<html><body><h1>BizLens AI API is running. Visit /docs</h1></body></html>"
