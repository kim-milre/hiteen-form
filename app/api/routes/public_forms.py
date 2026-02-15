from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.forms import FormCreate, FormAdminOut, FormPublicOut
from app.schemas.responses import ResponseCreate, ResponseOut
from app.services import form_service, response_service

router = APIRouter(prefix="/api/forms", tags=["public"])

@router.post("", response_model=FormAdminOut)
def create_form(payload: FormCreate, db: Session = Depends(get_db)):
    form = form_service.create_form(
        db=db,
        title=payload.title,
        description=payload.description,
        questions=[q.model_dump() for q in payload.questions],
    )
    return FormAdminOut(
        id=form.id,
        title=form.title,
        description=form.description,
        public_slug=form.public_slug,
        admin_token=form.admin_token,
        is_open=form.is_open,
        questions=[
            {
                "id": q.id,
                "order_index": q.order_index,
                "type": q.type,
                "title": q.title,
                "required": q.required,
                "config_json": q.config_json,
            }
            for q in sorted(form.questions, key=lambda x: x.order_index)
        ],
    )

@router.get("/by-slug/{slug}", response_model=FormPublicOut)
def get_form_by_slug(slug: str, db: Session = Depends(get_db)):
    form = form_service.get_form_by_slug(db, slug)
    if not form:
        raise HTTPException(status_code=404, detail="form not found")
    return FormPublicOut(
        id=form.id,
        title=form.title,
        description=form.description,
        public_slug=form.public_slug,
        is_open=form.is_open,
        questions=[
            {
                "id": q.id,
                "order_index": q.order_index,
                "type": q.type,
                "title": q.title,
                "required": q.required,
                "config_json": q.config_json,
            }
            for q in sorted(form.questions, key=lambda x: x.order_index)
        ],
    )

@router.post("/by-slug/{slug}/responses", response_model=ResponseOut)
def submit_response(slug: str, payload: ResponseCreate, db: Session = Depends(get_db)):
    form = form_service.get_form_by_slug(db, slug)
    if not form:
        raise HTTPException(status_code=404, detail="form not found")
    resp = response_service.create_response(db, form, [a.model_dump() for a in payload.answers])
    return ResponseOut(id=resp.id, submitted_at=resp.submitted_at.isoformat())