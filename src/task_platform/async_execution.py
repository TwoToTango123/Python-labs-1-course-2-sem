"""Асинхронный исполнитель задач с расширяемыми обработчиками."""

from __future__ import annotations

import asyncio
import logging
from contextlib import AsyncExitStack, AbstractAsyncContextManager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from .contracts import AsyncTaskHandlerProtocol
from .exceptions import (
    TaskAlreadyCompletedError,
    TaskExecutionError,
    TaskExecutorNotRunningError,
    TaskHandlerNotFoundError,
)
from .task_types import Task, TaskStatus

TaskMatcher = Callable[[Task], bool]


@dataclass(slots=True, frozen=True)
class TaskExecutionResult:
    """Результат обработки одной задачи."""

    task_id: str
    handler_name: str
    success: bool
    message: str
    started_at: datetime
    finished_at: datetime
    error_type: str | None = None


@dataclass(slots=True, frozen=True)
class _HandlerRegistration:
    name: str
    matcher: TaskMatcher
    handler: AsyncTaskHandlerProtocol


@dataclass(slots=True)
class TaskExecutionStats:
    """Сводная статистика по сессии выполнения."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0


_STOP_SIGNAL = object()


class AsyncTaskExecutor(AbstractAsyncContextManager["AsyncTaskExecutor"]):
    """Асинхронный исполнитель задач на базе asyncio.Queue и worker-пула."""

    def __init__(
        self,
        worker_count: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        if worker_count < 1:
            raise ValueError("worker_count должен быть >= 1")

        self._worker_count = worker_count
        self._logger = logger or logging.getLogger("task_platform.executor")
        self._queue: asyncio.Queue[Task | object] = asyncio.Queue()
        self._registrations: list[_HandlerRegistration] = []
        self._workers: list[asyncio.Task[None]] = []
        self._results: list[TaskExecutionResult] = []
        self._stats = TaskExecutionStats()
        self._running = False
        self._exit_stack = AsyncExitStack()

    @property
    def stats(self) -> TaskExecutionStats:
        """Текущая статистика выполнения."""

        return self._stats

    @property
    def results(self) -> tuple[TaskExecutionResult, ...]:
        """Снимок накопленных результатов выполнения."""

        return tuple(self._results)

    def register_handler(
        self,
        name: str,
        handler: AsyncTaskHandlerProtocol,
        matcher: TaskMatcher,
    ) -> None:
        """Зарегистрировать обработчик и правило маршрутизации задачи."""

        if not name.strip():
            raise ValueError("name не может быть пустым")
        self._registrations.append(
            _HandlerRegistration(name=name.strip(), matcher=matcher, handler=handler)
        )

    async def __aenter__(self) -> AsyncTaskExecutor:
        if self._running:
            return self

        for registration in self._registrations:
            if isinstance(registration.handler, AbstractAsyncContextManager):
                await self._exit_stack.enter_async_context(registration.handler)

        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(index), name=f"task-worker-{index}")
            for index in range(1, self._worker_count + 1)
        ]
        self._logger.info("Executor started with %s workers", self._worker_count)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if not self._running:
            return

        for _ in self._workers:
            await self._queue.put(_STOP_SIGNAL)

        await self._queue.join()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        self._running = False
        await self._exit_stack.aclose()
        self._exit_stack = AsyncExitStack()

        self._logger.info(
            "Executor stopped. total=%s succeeded=%s failed=%s",
            self._stats.total,
            self._stats.succeeded,
            self._stats.failed,
        )

    async def submit(self, task: Task) -> None:
        """Добавить задачу в асинхронную очередь исполнения."""

        if not self._running:
            raise TaskExecutorNotRunningError("Исполнитель не запущен")

        await self._queue.put(task)

    async def run(self, tasks: list[Task]) -> list[TaskExecutionResult]:
        """Выполнить список задач внутри жизненного цикла async-контекста."""

        async with self:
            for task in tasks:
                await self.submit(task)
            await self.wait_until_idle()
        return list(self._results)

    async def wait_until_idle(self) -> None:
        """Дождаться обработки всех задач из очереди."""

        if not self._running:
            raise TaskExecutorNotRunningError("Исполнитель не запущен")
        await self._queue.join()

    def _resolve_handler(self, task: Task) -> _HandlerRegistration:
        for registration in self._registrations:
            if registration.matcher(task):
                return registration

        raise TaskHandlerNotFoundError(
            f"Не найден обработчик для задачи {task.id!r}"
        )

    async def _worker(self, worker_id: int) -> None:
        self._logger.debug("Worker %s started", worker_id)

        while True:
            queue_item = await self._queue.get()
            try:
                if queue_item is _STOP_SIGNAL:
                    break

                task = queue_item
                if not isinstance(task, Task):
                    self._logger.error("Unexpected queue item type: %s", type(task))
                    continue

                result = await self._execute_task(task)
                self._results.append(result)
            finally:
                self._queue.task_done()

        self._logger.debug("Worker %s finished", worker_id)

    async def _execute_task(self, task: Task) -> TaskExecutionResult:
        started_at = datetime.now(timezone.utc)

        try:
            registration = self._resolve_handler(task)
            self._prepare_task_for_execution(task)

            self._logger.info(
                "Task %s started by handler %s",
                task.id,
                registration.name,
            )
            message = await registration.handler.handle(task)
            task.mark_done()

            finished_at = datetime.now(timezone.utc)
            self._stats.total += 1
            self._stats.succeeded += 1
            self._logger.info(
                "Task %s completed by handler %s",
                task.id,
                registration.name,
            )
            return TaskExecutionResult(
                task_id=task.id,
                handler_name=registration.name,
                success=True,
                message=message,
                started_at=started_at,
                finished_at=finished_at,
            )
        except Exception as error:  # noqa: BLE001
            finished_at = datetime.now(timezone.utc)
            self._stats.total += 1
            self._stats.failed += 1
            self._logger.exception("Task %s failed", task.id)

            return TaskExecutionResult(
                task_id=task.id,
                handler_name=self._safe_handler_name(task),
                success=False,
                message=str(error),
                started_at=started_at,
                finished_at=finished_at,
                error_type=type(error).__name__,
            )

    def _safe_handler_name(self, task: Task) -> str:
        try:
            return self._resolve_handler(task).name
        except TaskExecutionError:
            return "<unresolved>"

    @staticmethod
    def _prepare_task_for_execution(task: Task) -> None:
        if task.status is TaskStatus.DONE:
            raise TaskAlreadyCompletedError(
                f"Задача {task.id!r} уже завершена"
            )

        if task.status is TaskStatus.DRAFT:
            task.status = TaskStatus.READY

        if not task.is_ready_for_execution:
            raise TaskExecutionError(
                f"Задача {task.id!r} не готова к выполнению"
            )

        task.mark_in_progress()
