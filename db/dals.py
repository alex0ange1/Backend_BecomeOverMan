from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.models import User


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, username: str, hashed_password: str, password: str) -> User:
        try:
            new_user = User(username=username, hashed_password=hashed_password, password=password)
            self.db_session.add(new_user)
            await self.db_session.flush()
            return new_user
        except IntegrityError:
            # Обработка случая, когда username не уникален
            # Возможно, здесь нужно вернуть ошибку или выполнить другие действия
            raise Exception("Username must be unique")  # Пример

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_username(self, username: str) -> Union[User, None]:
        query = select(User).where(User.username == username)
        result = await self.db_session.execute(query)
        user_row = result.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[UUID, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        update_data = {}

        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(**update_data, **kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]

    async def add_task_to_user(self, user_id: UUID, task: str):
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(pending_tasks=func.array_append(User.pending_tasks, task))
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        updated_user_id = result.scalar()
        return updated_user_id

    async def remove_task_from_user(self, user_id: UUID, task: str):
        pending_tasks = case(
            [
                (
                    func.array_position(User.pending_tasks, task) > 0,
                    func.array_remove(User.pending_tasks, task),
                ),
            ],
            else_=User.pending_tasks,
        )

        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(pending_tasks=pending_tasks)
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        updated_user_id = result.scalar()
        return updated_user_id

    async def complete_task(self, user_id: UUID, task: str):
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(pending_tasks=func.array_remove(User.pending_tasks, task))
            .values(completed_tasks=func.array_append(User.completed_tasks, task))
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        completed_user_id = result.scalar()
        return completed_user_id

    async def uncomplete_task(self, user_id: UUID, task: str):
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(completed_tasks=func.array_remove(User.completed_tasks, task))
            .values(pending_tasks=func.array_append(User.pending_tasks, task))
            .returning(User.user_id)
        )
        result = await self.db_session.execute(query)
        uncompleted_user_id = result.scalar()
        return uncompleted_user_id

    async def verify_password(self, username: str, password: str) -> Union[UUID, None]:
        query = select(User).where(User.username == username, User.password == password)
        user = await self.db_session.execute(query)
        user = user.scalars().first()
        if user:
            return user.user_id
        else:
            return None


