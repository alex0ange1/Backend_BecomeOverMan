from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import AddTaskRequest
from api.models import AddTaskResponse
from api.models import CompleteTaskResponse
from api.models import DeleteUserResponse
from api.models import RemoveTaskResponse
from api.models import ShowUser
from api.models import UncompleteTaskResponse
from api.models import UpdatedUserRequest
from api.models import UpdatedUserResponse
from api.models import UserCreate
from db.dals import UserDAL
from db.session import get_db
from hashing import Hasher

user_router = APIRouter()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                username=body.username,
                hashed_password=Hasher.get_password_hash(body.password),
            )
            return ShowUser(
                user_id=user.user_id,
                username=user.username,
                is_active=user.is_active,
            )


async def _delete_user(user_id, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = await user_dal.delete_user(
                user_id=user_id,
            )
            return deleted_user_id


async def _add_task(user_id: UUID, task: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            added_user_id = await user_dal.add_task_to_user(user_id=user_id, task=task)
            return added_user_id


async def _complete_task(user_id: UUID, task: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            completed_user_id = await user_dal.complete_task(user_id=user_id, task=task)
            return completed_user_id


async def _uncomplete_task(user_id: UUID, task: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            uncompleted_user_id = await user_dal.uncomplete_task(
                user_id=user_id, task=task
            )
            return uncompleted_user_id


async def _remove_task(user_id: UUID, task: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            removedtask_user_id = await user_dal.remove_task_from_user(
                user_id=user_id, task=task
            )
            return removedtask_user_id


async def _get_user_by_id(user_id, db) -> Union[ShowUser, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(
                user_id=user_id,
            )
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    username=user.username,
                    is_active=user.is_active,
                )


async def _update_user(
    updated_user_params: dict, user_id: UUID, db
) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update_user(
                user_id=user_id,
                **updated_user_params,
            )
            return updated_user_id


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )
    return user


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
    user_id: UUID, body: UpdatedUserRequest, db: AsyncSession = Depends(get_db)
) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_unset=True)
    if not updated_user_params:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided!",
        )
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )
    updated_user_id = await _update_user(
        updated_user_params=updated_user_params, db=db, user_id=user_id
    )
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.post("/{user_id}/add_task", response_model=AddTaskResponse)
async def add_task_to_user(
    user_id: UUID, task_request: AddTaskRequest, db: AsyncSession = Depends(get_db)
) -> AddTaskResponse:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )
    return AddTaskResponse(task=task_request.task)


@user_router.post("/{user_id}/remove_task", response_model=RemoveTaskResponse)
async def remove_task_from_user(
    user_id: UUID, task_request: RemoveTaskResponse, db: AsyncSession = Depends(get_db)
) -> RemoveTaskResponse:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )
    removed_task_id = await _remove_task(user_id=user_id, task=task_request.task, db=db)
    if removed_task_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_request.task}' not found for user with id {user_id}",
        )

    return RemoveTaskResponse(task=task_request.task)


@user_router.post("/{user_id}/complete_task", response_model=CompleteTaskResponse)
async def complete_task(
    user_id: UUID,
    task_request: CompleteTaskResponse,
    db: AsyncSession = Depends(get_db),
) -> CompleteTaskResponse:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )

    completed_task_id = await _complete_task(
        user_id=user_id, task=task_request.task, db=db
    )
    if completed_task_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_request.task}' not found for user with id {user_id}",
        )

    return CompleteTaskResponse(task=task_request.task)


@user_router.post("/{user_id}/uncomplete_task", response_model=UncompleteTaskResponse)
async def uncomplete_task(
    user_id: UUID,
    task_request: UncompleteTaskResponse,
    db: AsyncSession = Depends(get_db),
) -> UncompleteTaskResponse:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} is not found!"
        )

    uncompleted_task_id = await _uncomplete_task(
        user_id=user_id, task=task_request.task, db=db
    )
    if uncompleted_task_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_request.task}' not found for user with id {user_id}",
        )

    return UncompleteTaskResponse(task=task_request.task)
