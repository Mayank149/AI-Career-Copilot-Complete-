from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.resume import router as resume_router
from routes import review

app = FastAPI(title="AI Career Copilot API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)
app.include_router(
    review.router,
    tags=["ATS Checker"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI Career Copilot API"}

# Mount frontend static files if available
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


