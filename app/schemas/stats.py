from pydantic import BaseModel

class ChoiceCount(BaseModel):
    option: str
    count: int

class QuestionStat(BaseModel):
    question_id: str
    type: str
    title: str
    total_answers: int
    choice_counts: list[ChoiceCount] | None = None
    scale_avg: float | None = None
    scale_min: int | None = None
    scale_max: int | None = None

class FormStatsOut(BaseModel):
    form_id: str
    responses_total: int
    questions: list[QuestionStat]