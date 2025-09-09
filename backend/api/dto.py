from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"

    def __str__(self):
        return self.value


class HistoryMessage(BaseModel):
    role: Role
    content: str
    timestamp: int | None = None


class ChatRequest(BaseModel):
    query: str
    # history: list[lb.RecStrDict]
    # history: list[History]
    shell_history: str


class AuthenticationResponse(BaseModel):
    code: str
    name: str
    email: str


class AuthenticationRequest(BaseModel):
    email: str
    password: str
