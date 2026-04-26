from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    k: int = 3