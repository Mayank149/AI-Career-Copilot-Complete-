from fastapi import FastAPI, UploadFile, File
from routes.resume import router as resume_router

app = FastAPI()

app.include_router(resume_router)

@app.get("/")
def home():
    return {"message": "AI Career Copilot API"}

