"""Источник задач, генерирующий задачи программно."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from ..task_types import Task, TaskStatus


class GeneratorTaskSource:
    """Генерирует фиксированное количество задач."""

    def __init__(
        self,
        count: int,
        description_factory: Callable[[int], str] | None = None,
        priority_factory: Callable[[int], int] | None = None,
        status_factory: Callable[[int], TaskStatus] | None = None,
        id_prefix: str = "generated",
    ) -> None:
        if count < 0:
            raise ValueError("count должен быть неотрицательным")

        self._count = count
        self._description_factory = description_factory or (
            lambda i: f"Сгенерированная задача #{i + 1}"
        )
        self._priority_factory = priority_factory or (lambda i: (i % 10) + 1)
        self._status_factory = status_factory or (lambda i: TaskStatus.READY)
        self._id_prefix = id_prefix

    def get_tasks(self) -> list[Task]:
        tasks: list[Task] = []
        base_created_at = datetime.now(timezone.utc)
        for i in range(self._count):
            tasks.append(
                Task(
                    id=f"{self._id_prefix}-{i + 1}",
                    description=self._description_factory(i),
                    priority=self._priority_factory(i),
                    status=self._status_factory(i),
                    created_at=base_created_at + timedelta(seconds=i),
                )
            )
        return tasks
