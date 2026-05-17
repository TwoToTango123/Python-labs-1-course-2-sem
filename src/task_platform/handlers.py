"""Базовые расширяемые async-обработчики задач."""

from __future__ import annotations

import asyncio
from contextlib import AbstractAsyncContextManager

from .task_types import Task


class BaseAsyncTaskHandler(AbstractAsyncContextManager["BaseAsyncTaskHandler"]):
    """Базовый обработчик с async-контекстом для управления ресурсами."""

    def __init__(self) -> None:
        self._opened = False

    async def __aenter__(self) -> BaseAsyncTaskHandler:
        self._opened = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self._opened = False

    @property
    def is_open(self) -> bool:
        """Признак открытого ресурса обработчика."""

        return self._opened

    def _ensure_open(self) -> None:
        if not self._opened:
            raise RuntimeError("Handler resource is not opened")


class SleepTaskHandler(BaseAsyncTaskHandler):
    """Обработчик, имитирующий I/O-работу через asyncio.sleep."""

    def __init__(self, delay_seconds: float = 0.05) -> None:
        super().__init__()
        if delay_seconds < 0:
            raise ValueError("delay_seconds должен быть >= 0")
        self._delay_seconds = delay_seconds

    async def handle(self, task: Task) -> str:
        self._ensure_open()
        await asyncio.sleep(self._delay_seconds)
        return f"Task {task.id} processed with simulated I/O"


class FailingTaskHandler(BaseAsyncTaskHandler):
    """Обработчик, который предсказуемо завершает обработку ошибкой."""

    async def handle(self, task: Task) -> str:
        self._ensure_open()
        await asyncio.sleep(0)
        raise RuntimeError(f"Intentional handler failure for task {task.id}")
