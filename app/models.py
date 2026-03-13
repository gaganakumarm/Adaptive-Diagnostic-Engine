from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Question(BaseModel):
    id: Optional[str] = None
    question: str
    options: List[str]
    correct_answer: str
    difficulty: float = Field(ge=0.1, le=1.0)
    topic: str
    tags: List[str]

class UserSession(BaseModel):
    session_id: str
    ability_score: float = Field(default=0.5, ge=0.1, le=1.0)
    questions_answered: List[str] = []
    correct_answers: int = 0
    total_questions: int = 0
    weak_topics: Dict[str, int] = {}
    ability_history: List[float] = []

class AnswerSubmission(BaseModel):
    session_id: str
    question_id: str
    answer: str

class AdaptiveResponse(BaseModel):
    question: Question
    question_number: int
    current_ability: float

class AnswerResult(BaseModel):
    correct: bool
    updated_ability: float
    question_number: int
