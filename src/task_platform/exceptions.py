"""Специализированные исключения доменной модели задач."""

from __future__ import annotations


class TaskError(Exception):
    """Базовое исключение платформы задач."""


class TaskValidationError(TaskError, ValueError):
    """Ошибка валидации значения атрибута задачи."""


class TaskStateTransitionError(TaskError):
    """Ошибка недопустимого перехода состояния задачи."""


class InvalidTaskIdError(TaskValidationError):
    def __init__(self, field_name: str = "id") -> None:
        super().__init__(f"Некорректное значение поля '{field_name}'")


class InvalidTaskDescriptionError(TaskValidationError):
    def __init__(self, field_name: str = "description") -> None:
        super().__init__(f"Некорректное значение поля '{field_name}'")


class InvalidTaskPriorityError(TaskValidationError):
    def __init__(self, message: str = "Некорректное значение priority") -> None:
        super().__init__(message)


class InvalidTaskStatusError(TaskValidationError):
    def __init__(self, message: str = "Некорректное значение status") -> None:
        super().__init__(message)


class InvalidTaskCreatedAtError(TaskValidationError):
    def __init__(self, message: str = "Некорректное значение created_at") -> None:
        super().__init__(message)


class TaskExecutionError(TaskError):
    """Базовая ошибка выполнения задачи в асинхронном исполнителе."""


class TaskHandlerNotFoundError(TaskExecutionError):
    """Не найден обработчик, способный обработать задачу."""


class TaskAlreadyCompletedError(TaskExecutionError):
    """Попытка повторно обработать уже завершенную задачу."""


class TaskExecutorNotRunningError(TaskExecutionError):
    """Операция требует запущенного async-исполнителя."""