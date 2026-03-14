"""Пакет платформы обработки задач. Лабораторная работа №1."""

from .contracts import TaskSourceProtocol
from .intake import collect_tasks, collect_tasks_from_source
from .task_types import Task, TaskId

__all__ = [
    "Task",
    "TaskId",
    "TaskSourceProtocol",
    "collect_tasks",
    "collect_tasks_from_source",
]
