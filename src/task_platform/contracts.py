"""Поведенческие контракты для источников задач."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .task_types import Task


@runtime_checkable
class TaskSourceProtocol(Protocol):
    """Контракт для любого объекта, способного предоставлять задачи."""

    def get_tasks(self) -> list[Task]:
        """Вернуть список задач из источника."""
