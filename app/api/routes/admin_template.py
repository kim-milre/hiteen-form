from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional
from openpyxl import Workbook

from app.db.mongo import db, ADMIN_TOKEN

router = APIRouter()

def require_admin(token: str):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="invalid admin token")

@router.get("/responses")
async def admin_list_responses(
    token: str = Query(...),
    limit: int = 200,
    skip: int = 0,
):
    require_admin(token)

    cursor = (
        db.template_responses
        .find({}, {"_id": 1, "name": 1, "studentId": 1, "number": 1, "major": 1, "interest": 1, "paymentStatus": 1, "created_at": 1})
        .sort("created_at", -1)
        .skip(skip)
        .limit(min(limit, 1000))
    )

    items: List[Dict[str, Any]] = []
    async for r in cursor:
        r["_id"] = str(r["_id"])
        if isinstance(r.get("created_at"), datetime):
            r["created_at"] = r["created_at"].isoformat()
        items.append(r)

    total = await db.template_responses.count_documents({})
    return {"total": total, "skip": skip, "limit": limit, "items": items}

@router.get("/stats")
async def admin_stats(token: str = Query(...)):
    require_admin(token)

    total = await db.template_responses.count_documents({})

    pipeline_interest = [
        {"$unwind": {"path": "$interest", "preserveNullAndEmptyArrays": False}},
        {"$group": {"_id": "$interest", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    pipeline_payment = [
        {"$group": {"_id": "$paymentStatus", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    interest_counts: List[Dict[str, Any]] = []
    async for d in db.template_responses.aggregate(pipeline_interest):
        interest_counts.append({"option": d["_id"], "count": d["count"]})

    payment_counts: List[Dict[str, Any]] = []
    async for d in db.template_responses.aggregate(pipeline_payment):
        key = d["_id"] if d["_id"] else ""
        payment_counts.append({"option": key, "count": d["count"]})

    return {
        "total_responses": total,
        "interest_counts": interest_counts,
        "payment_counts": payment_counts,
    }

@router.get("/export")
async def admin_export_excel(token: str = Query(...)):
    require_admin(token)

    wb = Workbook()
    ws = wb.active
    ws.title = "template_responses"

    ws.append(["이름", "학번", "전화번호", "전공", "관심분야", "납부상태", "제출시간"])

    cursor = db.template_responses.find({}).sort("created_at", 1)
    async for r in cursor:
        created_at = r.get("created_at")
        created_at_str = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at) if created_at else ""

        ws.append([
            r.get("name", ""),
            r.get("studentId", ""),
            r.get("number", ""),
            r.get("major", ""),
            ", ".join(r.get("interest", []) or []),
            r.get("paymentStatus", ""),
            created_at_str,
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=template_responses.xlsx"},
    )