import re
import uuid
from typing import List
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class ShowUser(TunedModel):
    user_id = uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool
    сompleted_tasks: Optional[List[str]]
    pending_tasks: Optional[List[str]]


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters"
            )
        return value

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class AddTaskResponse(BaseModel):
    task: str


class RemoveTaskResponse(BaseModel):
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
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters"
            )
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
