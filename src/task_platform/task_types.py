"""Доменная модель задачи и вспомогательные дескрипторы."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .exceptions import (
    InvalidTaskCreatedAtError,
    InvalidTaskDescriptionError,
    InvalidTaskIdError,
    InvalidTaskPriorityError,
    InvalidTaskStatusError,
    TaskStateTransitionError,
)

TaskId = str
TaskDescription = str


class TaskStatus(str, Enum):
    """Возможные статусы задачи."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class _TaskDescriptor:
    """Базовый data descriptor с приватным хранилищем значения."""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[object]) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance: object, value: Any) -> None:
        setattr(instance, self.private_name, self.validate(instance, value))

    def validate(self, instance: object, value: Any) -> Any:
        return value


class _StringField(_TaskDescriptor):
    def __init__(self, error_type: type[ValueError]) -> None:
        self._error_type = error_type

    def validate(self, instance: object, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise self._error_type(self.public_name)
        return value.strip()


class _PriorityField(_TaskDescriptor):
    def validate(self, instance: object, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidTaskPriorityError("priority должен быть целым числом")
        if value < 1 or value > 10:
            raise InvalidTaskPriorityError("priority должен быть в диапазоне от 1 до 10")
        return value


class _StatusField(_TaskDescriptor):
    _allowed_transitions: dict[TaskStatus, set[TaskStatus]] = {
        TaskStatus.DRAFT: {TaskStatus.READY},
        TaskStatus.READY: {TaskStatus.IN_PROGRESS, TaskStatus.DONE},
        TaskStatus.IN_PROGRESS: {TaskStatus.DONE},
        TaskStatus.DONE: set(),
    }

    def validate(self, instance: object, value: Any) -> TaskStatus:
        if isinstance(value, str):
            try:
                value = TaskStatus(value)
            except ValueError as error:
                raise InvalidTaskStatusError(
                    "status должен быть одним из: draft, ready, in_progress, done"
                ) from error

        if not isinstance(value, TaskStatus):
            raise InvalidTaskStatusError(
                "status должен быть одним из: draft, ready, in_progress, done"
            )

        current_status = getattr(instance, self.private_name, None)
        if current_status is not None and value != current_status:
            allowed = self._allowed_transitions[current_status]
            if value not in allowed:
                raise TaskStateTransitionError(
                    f"Нельзя перевести задачу из статуса {current_status.value} в {value.value}"
                )

        return value


class _CreatedAtField(_TaskDescriptor):
    def validate(self, instance: object, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as error:
                raise InvalidTaskCreatedAtError(
                    "created_at должен быть datetime или ISO-строкой"
                ) from error

        if not isinstance(value, datetime):
            raise InvalidTaskCreatedAtError(
                "created_at должен быть datetime или ISO-строкой"
            )

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class _ReadinessDescriptor:
    """Non-data descriptor: вычисляет готовность и может быть перекрыт атрибутом экземпляра."""

    def __get__(self, instance: object | None, owner: type[object]) -> Any:
        if instance is None:
            return self
        return instance.status in {TaskStatus.READY, TaskStatus.IN_PROGRESS}


@dataclass(frozen=True, slots=True)
class TaskSnapshot:
    """Неизменяемое представление задачи для сравнения и сериализации."""

    id: TaskId
    description: TaskDescription
    priority: int
    status: TaskStatus
    created_at: datetime


class Task:
    """Доменная модель задачи с валидацией через дескрипторы.

    Data descriptors защищают обязательные поля, а `readiness` показывает
    non-data descriptor: значение вычисляется на лету и может быть перекрыто
    атрибутом экземпляра при намеренном нарушении инкапсуляции.
    """

    id = _StringField(InvalidTaskIdError)
    description = _StringField(InvalidTaskDescriptionError)
    priority = _PriorityField()
    status = _StatusField()
    created_at = _CreatedAtField()
    readiness = _ReadinessDescriptor()

    def __init__(
        self,
        id: TaskId,
        description: TaskDescription,
        priority: int,
        status: TaskStatus | str = TaskStatus.READY,
        created_at: datetime | str | None = None,
    ) -> None:
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)

    @property
    def is_ready_for_execution(self) -> bool:
        """Публичное вычисляемое свойство для безопасной проверки готовности."""

        return self.status in {TaskStatus.READY, TaskStatus.IN_PROGRESS}

    @property
    def is_done(self) -> bool:
        """Признак завершённой задачи."""

        return self.status is TaskStatus.DONE

    def mark_in_progress(self) -> None:
        """Перевести задачу в статус выполнения."""

        self.status = TaskStatus.IN_PROGRESS

    def mark_done(self) -> None:
        """Перевести задачу в статус завершения."""

        self.status = TaskStatus.DONE

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать задачу в JSON-friendly словарь."""

        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Task":
        """Создать задачу из сырого словаря с обязательной валидацией."""

        if "id" not in data:
            raise InvalidTaskIdError()
        if "description" not in data and "payload" not in data:
            raise InvalidTaskDescriptionError()
        if "priority" not in data:
            raise InvalidTaskPriorityError()

        description = data.get("description", data.get("payload"))

        return cls(
            id=data["id"],
            description=description,
            priority=data["priority"],
            status=data.get("status", TaskStatus.READY),
            created_at=data.get("created_at"),
        )

    @property
    def snapshot(self) -> TaskSnapshot:
        """Неизменяемое представление для сравнения и тестов."""

        return TaskSnapshot(
            id=self.id,
            description=self.description,
            priority=self.priority,
            status=self.status,
            created_at=self.created_at,
        )

    def __repr__(self) -> str:
        return (
            "Task("
            f"id={self.id!r}, description={self.description!r}, priority={self.priority!r}, "
            f"status={self.status.value!r}, created_at={self.created_at.isoformat()!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.snapshot == other.snapshot
