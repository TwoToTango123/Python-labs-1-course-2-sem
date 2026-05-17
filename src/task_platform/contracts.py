"""Поведенческие контракты для источников задач и async-обработчиков."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .task_types import Task


@runtime_checkable
class TaskSourceProtocol(Protocol):
    """Контракт для любого объекта, способного предоставлять задачи."""

    def get_tasks(self) -> list[Task]:
        """Вернуть список задач из источника."""


@runtime_checkable
class AsyncTaskHandlerProtocol(Protocol):
    """Контракт асинхронного обработчика задач."""

    async def handle(self, task: Task) -> str:
        """Асинхронно обработать задачу и вернуть краткий результат."""
