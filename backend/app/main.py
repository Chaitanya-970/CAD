from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import villages, alert, query, crop, flood, safezone, sms, sos

app = FastAPI(title="AFIP API", version="0.1.0")

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
