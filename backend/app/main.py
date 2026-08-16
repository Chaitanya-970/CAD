from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from app.routes import villages, alert, query, crop, flood, safezone, sms, sos

logger = logging.getLogger("afip")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="AFIP API", version="0.1.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.0f}ms)")
    return response

# Configure CORS for localhost:3000 (Next.js frontend) per spec
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(villages.router, tags=["Villages"])
app.include_router(alert.router, tags=["Alerts"])
app.include_router(query.router, tags=["AI Query"])
app.include_router(crop.router, tags=["Crop Assessment"])
app.include_router(flood.router, tags=["Flood Prediction"])
app.include_router(safezone.router, tags=["Safe Zones"])
app.include_router(sms.router, tags=["SMS Webhook"])
app.include_router(sos.router, tags=["SOS Dashboard"])

@app.get("/")
async def root():
    return {"status": "AFIP Backend is running"}
