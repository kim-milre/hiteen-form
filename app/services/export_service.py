from io import BytesIO
from sqlalchemy.orm import Session
from openpyxl import Workbook
from app.db import models
from collections import defaultdict

def export_form_xlsx(db: Session, form: models.Form) -> bytes:
    questions = sorted(form.questions, key=lambda x: x.order_index)

    responses = db.query(models.Response).filter(models.Response.form_id == form.id).all()
    answers = db.query(models.Answer).join(models.Response).filter(models.Response.form_id == form.id).all()

    ans_map: dict[str, dict[str, models.Answer]] = defaultdict(dict)
    for a in answers:
        ans_map[a.response_id][a.question_id] = a

    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"

    header = ["submitted_at"] + [q.title for q in questions]
    ws.append(header)

    for r in responses:
        row = [r.submitted_at.isoformat()]
        amap = ans_map.get(r.id, {})
        for q in questions:
            a = amap.get(q.id)
            if not a:
                row.append("")
                continue
            if q.type == "multi_choice" and isinstance(a.value_json, list):
                row.append(";".join(str(x) for x in a.value_json))
            elif q.type == "linear_scale" and a.numeric_value is not None:
                row.append(a.numeric_value)
            elif a.value_text is not None:
                row.append(a.value_text)
            elif a.value_json is not None:
                row.append(str(a.value_json))
            else:
                row.append("")
        ws.append(row)

    wsq = wb.create_sheet("Questions")
    wsq.append(["order", "question_id", "type", "title", "required", "config_json"])
    for q in questions:
        wsq.append([q.order_index, q.id, q.type, q.title, q.required, str(q.config_json or "")])

    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()