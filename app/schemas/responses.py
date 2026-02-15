from pydantic import BaseModel

class AnswerIn(BaseModel):
    question_id: str
    value_text: str | None = None
    value_json: dict | list | None = None
    numeric_value: int | None = None

class ResponseCreate(BaseModel):
    answers: list[AnswerIn]

class ResponseOut(BaseModel):
    id: str
    submitted_at: str