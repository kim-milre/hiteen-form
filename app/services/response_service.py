from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db import models

def _validate_required(form: models.Form, answers_in: list[dict]):
    answer_map = {a["question_id"]: a for a in answers_in}
    for q in form.questions:
        if not q.required:
            continue
        a = answer_map.get(q.id)
        if not a:
            raise HTTPException(status_code=400, detail=f"missing required answer: {q.id}")
        has_text = a.get("value_text") is not None and str(a.get("value_text")).strip() != ""
        has_json = a.get("value_json") is not None
        has_num = a.get("numeric_value") is not None
        if not (has_text or has_json or has_num):
            raise HTTPException(status_code=400, detail=f"empty required answer: {q.id}")

def create_response(db: Session, form: models.Form, answers_in: list[dict]) -> models.Response:
    if not form.is_open:
        raise HTTPException(status_code=400, detail="form closed")

    _validate_required(form, answers_in)

    resp = models.Response(form_id=form.id)
    db.add(resp)
    db.flush()

    for a in answers_in:
        db.add(
            models.Answer(
                response_id=resp.id,
                question_id=a["question_id"],
                value_text=a.get("value_text"),
                value_json=a.get("value_json"),
                numeric_value=a.get("numeric_value"),
            )
        )

    db.commit()
    db.refresh(resp)
    return resp