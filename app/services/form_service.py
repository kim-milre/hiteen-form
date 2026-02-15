import secrets
import string
from sqlalchemy.orm import Session
from app.db import models

def _rand_slug(n: int = 10) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

def _rand_token(n: int = 48) -> str:
    return secrets.token_urlsafe(n)[:64]

def create_form(db: Session, title: str, description: str | None, questions: list[dict]) -> models.Form:
    form = models.Form(
        title=title,
        description=description,
        public_slug=_rand_slug(),
        admin_token=_rand_token(),
        is_open=True,
    )
    for q in questions:
        form.questions.append(
            models.Question(
                order_index=q["order_index"],
                type=q["type"],
                title=q["title"],
                required=q["required"],
                config_json=q.get("config_json"),
            )
        )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form

def get_form_by_slug(db: Session, slug: str) -> models.Form | None:
    return db.query(models.Form).filter(models.Form.public_slug == slug).first()

def get_form_by_id(db: Session, form_id: str) -> models.Form | None:
    return db.query(models.Form).filter(models.Form.id == form_id).first()