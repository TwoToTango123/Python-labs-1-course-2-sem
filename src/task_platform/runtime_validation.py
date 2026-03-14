"""Runtime-проверки соответствия контракту источника и формату задачи."""

from __future__ import annotations

from typing import Any, TypeGuard

from .contracts import TaskSourceProtocol
from .task_types import Task


def is_task_source(obj: object) -> TypeGuard[TaskSourceProtocol]:
    """Вернуть True, если объект удовлетворяет контракту источника задач во время выполнения."""

    return isinstance(obj, TaskSourceProtocol)


def validate_task_dict(task: dict[str, Any]) -> Task:
    """Проверить обязательные поля задачи и вернуть нормализованную задачу."""

    if "id" not in task:
        raise ValueError("Задача должна содержать поле 'id'")
    if "payload" not in task:
        raise ValueError("Задача должна содержать поле 'payload'")
    if not isinstance(task["id"], str) or not task["id"]:
        raise ValueError("Поле 'id' задачи должно быть непустой строкой")

    return {"id": task["id"], "payload": task["payload"]}


def ensure_task_list(tasks: list[dict[str, Any]]) -> list[Task]:
    """Проверить список сырых словарей задач и вернуть нормализованный список."""

    return [validate_task_dict(task) for task in tasks]
