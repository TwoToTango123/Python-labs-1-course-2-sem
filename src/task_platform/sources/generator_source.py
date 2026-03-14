"""Источник задач, генерирующий задачи программно."""

from __future__ import annotations

from typing import Callable

from ..task_types import Task


class GeneratorTaskSource:
    """Генерирует фиксированное количество задач."""

    def __init__(
        self,
        count: int,
        payload_factory: Callable[[int], object] | None = None,
        id_prefix: str = "generated",
    ) -> None:
        if count < 0:
            raise ValueError("count должен быть неотрицательным")

        self._count = count
        self._payload_factory = payload_factory or (lambda i: {"index": i})
        self._id_prefix = id_prefix

    def get_tasks(self) -> list[Task]:
        tasks: list[Task] = []
        for i in range(self._count):
            tasks.append(
                {
                    "id": f"{self._id_prefix}-{i + 1}",
                    "payload": self._payload_factory(i),
                }
            )
        return tasks
