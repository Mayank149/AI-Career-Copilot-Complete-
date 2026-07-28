from fastapi import FastAPI, UploadFile, File
from routes.resume import router as resume_router
from routes import ats

app = FastAPI()

app.include_router(resume_router)
app.include_router(ats.router, prefix="/ats", tags=["ATS Checker"])

@app.get("/")
def home():
    return {"message": "AI Career Copilot API"}

