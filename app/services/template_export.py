from openpyxl import Workbook
from io import BytesIO
from fastapi.responses import StreamingResponse
from app.db.mongo import get_template_collection


async def export_template_excel():
    collection = get_template_collection()
    responses = await collection.find().to_list(length=None)

    wb = Workbook()
    ws = wb.active
    ws.title = "Template Responses"

    ws.append(["이름", "학번", "전화번호", "전공", "관심분야", "납부상태", "제출시간"])

    for r in responses:
        ws.append([
            r.get("name"),
            r.get("studentId"),
            r.get("number"),
            r.get("major"),
            ", ".join(r.get("interest", [])),
            r.get("paymentStatus"),
            str(r.get("created_at"))
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=template_responses.xlsx"},
    )