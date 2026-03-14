"""Определения типов задач, используемых во всём модуле."""

from __future__ import annotations

from typing import Any, TypedDict

TaskId = str


class Task(TypedDict):
    """Минимальное представление задачи для данной лабораторной работы."""

    id: TaskId
    payload: Any
