"""Модуль приёма задач, работающий с любым источником через контракт протокола."""

from __future__ import annotations

from collections.abc import Iterable

from .runtime_validation import is_task_source
from .task_types import Task


def collect_tasks_from_source(source: object) -> list[Task]:
    """Собрать задачи из единственного источника с runtime-проверкой контракта."""

    if not is_task_source(source):
        raise TypeError("Объект не реализует TaskSourceProtocol")

    return source.get_tasks()


def collect_tasks(sources: Iterable[object]) -> list[Task]:
    """Собрать задачи из нескольких источников, удовлетворяющих контракту."""

    result: list[Task] = []
    for source in sources:
        result.extend(collect_tasks_from_source(source))
    return result
