import re
import uuid
from typing import List
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class ShowUser(TunedModel):
    user_id = uuid.UUID
    username: str
    is_active: bool
    сompleted_tasks: Optional[List[str]]
    pending_tasks: Optional[List[str]]


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class LoginedUserResponse(BaseModel):
    logined_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class AddTaskResponse(BaseModel):
    task: str


class RemoveTaskResponse(BaseModel):
    task: str


class CompleteTaskResponse(BaseModel):
    task: str


class UncompleteTaskResponse(BaseModel):
    task: str


class AddTaskRequest(BaseModel):
    task: str

    @validator("task")
    def validate_task(cls, value):
        if not value:
            raise HTTPException(status_code=422, detail="Task should not be empty")
        # Добавьте любые другие проверки, которые вам нужны для задачи
        return value


class UpdatedUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]


class Token(BaseModel):
    access_token: str
    token_type: str
