"""Пакет платформы обработки задач. Лабораторная работа №2."""

from .contracts import TaskSourceProtocol
from .intake import collect_tasks, collect_tasks_from_source
from .exceptions import (
    InvalidTaskCreatedAtError,
    InvalidTaskDescriptionError,
    InvalidTaskIdError,
    InvalidTaskPriorityError,
    InvalidTaskStatusError,
    TaskError,
    TaskStateTransitionError,
    TaskValidationError,
)
from .task_types import Task, TaskDescription, TaskId, TaskStatus

__all__ = [
    "Task",
    "TaskDescription",
    "TaskId",
    "TaskStatus",
    "TaskError",
    "TaskValidationError",
    "TaskStateTransitionError",
    "InvalidTaskIdError",
    "InvalidTaskDescriptionError",
    "InvalidTaskPriorityError",
    "InvalidTaskStatusError",
    "InvalidTaskCreatedAtError",
    "TaskSourceProtocol",
    "collect_tasks",
    "collect_tasks_from_source",
]
