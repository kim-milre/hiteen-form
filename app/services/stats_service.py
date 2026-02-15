from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from app.db import models

def compute_stats(db: Session, form: models.Form) -> dict:
    responses = db.query(models.Response).filter(models.Response.form_id == form.id).all()
    answers = db.query(models.Answer).join(models.Response).filter(models.Response.form_id == form.id).all()

    answers_by_q: dict[str, list[models.Answer]] = defaultdict(list)
    for a in answers:
        answers_by_q[a.question_id].append(a)

    q_stats: list[dict] = []
    for q in sorted(form.questions, key=lambda x: x.order_index):
        arr = answers_by_q.get(q.id, [])
        base = {
            "question_id": q.id,
            "type": q.type,
            "title": q.title,
            "total_answers": len(arr),
            "choice_counts": None,
            "scale_avg": None,
            "scale_min": None,
            "scale_max": None,
        }

        if q.type in ["single_choice", "dropdown"]:
            c = Counter()
            for a in arr:
                if a.value_text:
                    c[a.value_text] += 1
            base["choice_counts"] = [{"option": k, "count": v} for k, v in c.most_common()]

        elif q.type == "multi_choice":
            c = Counter()
            for a in arr:
                if isinstance(a.value_json, list):
                    for opt in a.value_json:
                        c[str(opt)] += 1
            base["choice_counts"] = [{"option": k, "count": v} for k, v in c.most_common()]

        elif q.type == "linear_scale":
            nums = [a.numeric_value for a in arr if a.numeric_value is not None]
            if nums:
                base["scale_avg"] = sum(nums) / len(nums)
                base["scale_min"] = min(nums)
                base["scale_max"] = max(nums)

        q_stats.append(base)

    return {
        "form_id": form.id,
        "responses_total": len(responses),
        "questions": q_stats,
    }