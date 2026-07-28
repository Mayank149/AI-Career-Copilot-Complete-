from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ATSRequest(BaseModel):
    job_description: str

