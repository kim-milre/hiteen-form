from pydantic import BaseModel, Field
from typing import Literal

QuestionType = Literal[
    "short_text", "long_text", "single_choice", "multi_choice", "dropdown", "linear_scale", "date"
]

class QuestionCreate(BaseModel):
    order_index: int = 0
    type: QuestionType
    title: str
    required: bool = False
    config_json: dict | None = None

class FormCreate(BaseModel):
    title: str
    description: str | None = None
    questions: list[QuestionCreate] = Field(default_factory=list)

class QuestionOut(BaseModel):
    id: str
    order_index: int
    type: QuestionType
    title: str
    required: bool
    config_json: dict | None

class FormPublicOut(BaseModel):
    id: str
    title: str
    description: str | None
    public_slug: str
    is_open: bool
    questions: list[QuestionOut]

class FormAdminOut(FormPublicOut):
    admin_token: str