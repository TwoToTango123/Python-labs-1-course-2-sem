"""Пакет платформы обработки задач. Лабораторные работы по архитектуре Python."""

from .async_execution import AsyncTaskExecutor, TaskExecutionResult, TaskExecutionStats
from .contracts import AsyncTaskHandlerProtocol, TaskSourceProtocol
from .handlers import BaseAsyncTaskHandler, FailingTaskHandler, SleepTaskHandler
from .intake import collect_tasks, collect_tasks_from_source
from .exceptions import (
    InvalidTaskCreatedAtError,
    InvalidTaskDescriptionError,
    InvalidTaskIdError,
    InvalidTaskPriorityError,
    InvalidTaskStatusError,
    TaskAlreadyCompletedError,
    TaskError,
    TaskExecutionError,
    TaskExecutorNotRunningError,
    TaskHandlerNotFoundError,
    TaskStateTransitionError,
    TaskValidationError,
)
from .task_types import Task, TaskDescription, TaskId, TaskStatus
from .task_queue import TaskQueue

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
    "AsyncTaskHandlerProtocol",
    "collect_tasks",
    "collect_tasks_from_source",
    "TaskQueue",
    "TaskExecutionError",
    "TaskHandlerNotFoundError",
    "TaskAlreadyCompletedError",
    "TaskExecutorNotRunningError",
    "AsyncTaskExecutor",
    "TaskExecutionResult",
    "TaskExecutionStats",
    "BaseAsyncTaskHandler",
    "SleepTaskHandler",
    "FailingTaskHandler",
]
