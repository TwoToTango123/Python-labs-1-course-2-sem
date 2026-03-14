"""Источник задач, имитирующий внешний API-поставщик задач."""

from __future__ import annotations

from collections.abc import Callable

from ..runtime_validation import ensure_task_list
from ..task_types import Task


class ApiStubTaskSource:
    """Предоставляет задачи через вызываемую API-заглушку в памяти."""

    def __init__(self, fetcher: Callable[[], list[dict[str, object]]]) -> None:
        self._fetcher = fetcher

    def get_tasks(self) -> list[Task]:
        raw_tasks = self._fetcher()
        return ensure_task_list(raw_tasks)
