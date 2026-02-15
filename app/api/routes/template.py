from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.db.mongo import db

router = APIRouter()

class TemplateSubmit(BaseModel):
    studentId: str
    name: str
    major: str
    number: str
    interest: List[str]
    paymentStatus: str

@router.post("/submit")
async def submit_template(data: TemplateSubmit):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await db.template_responses.insert_one(doc)
    return {"success": True, "id": str(result.inserted_id)}