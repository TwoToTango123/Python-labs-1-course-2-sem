"""Тесты асинхронного исполнителя задач (ЛР4)."""

from __future__ import annotations

import asyncio
from time import perf_counter

import pytest

from task_platform import (
    AsyncTaskExecutor,
    BaseAsyncTaskHandler,
    FailingTaskHandler,
    SleepTaskHandler,
    Task,
    TaskExecutorNotRunningError,
    TaskStatus,
)


class RecordingHandler(BaseAsyncTaskHandler):
    """Тестовый обработчик, фиксирующий факт открытия ресурса."""

    def __init__(self) -> None:
        super().__init__()
        self.handled_ids: list[str] = []

    async def handle(self, task: Task) -> str:
        self._ensure_open()
        self.handled_ids.append(task.id)
        await asyncio.sleep(0)
        return f"handled:{task.id}"


def test_submit_requires_running_executor() -> None:
    executor = AsyncTaskExecutor(worker_count=1)
    task = Task(id="t1", description="task", priority=1)

    with pytest.raises(TaskExecutorNotRunningError):
        asyncio.run(executor.submit(task))


def test_executor_processes_tasks_and_marks_done() -> None:
    async def scenario() -> tuple[int, int, int, list[Task]]:
        tasks = [
            Task(id="io-1", description="a", priority=1),
            Task(id="io-2", description="b", priority=2),
            Task(id="io-3", description="c", priority=3),
        ]

        executor = AsyncTaskExecutor(worker_count=2)
        executor.register_handler(
            name="io",
            handler=SleepTaskHandler(delay_seconds=0.01),
            matcher=lambda _task: True,
        )

        results = await executor.run(tasks)
        return executor.stats.total, executor.stats.succeeded, len(results), tasks

    total, succeeded, result_count, tasks = asyncio.run(scenario())

    assert total == 3
    assert succeeded == 3
    assert result_count == 3
    assert all(task.status is TaskStatus.DONE for task in tasks)


def test_executor_routes_failures_and_collects_error_result() -> None:
    async def scenario() -> tuple[int, int, int, list[bool], list[str | None]]:
        tasks = [
            Task(id="ok-1", description="ok", priority=1),
            Task(id="fail-1", description="fail", priority=1),
        ]

        executor = AsyncTaskExecutor(worker_count=2)
        executor.register_handler(
            name="failing",
            handler=FailingTaskHandler(),
            matcher=lambda task: task.id.startswith("fail-"),
        )
        executor.register_handler(
            name="io",
            handler=SleepTaskHandler(delay_seconds=0),
            matcher=lambda _task: True,
        )

        results = await executor.run(tasks)
        return (
            executor.stats.total,
            executor.stats.succeeded,
            executor.stats.failed,
            [item.success for item in results],
            [item.error_type for item in results],
        )

    total, succeeded, failed, success_flags, error_types = asyncio.run(scenario())

    assert total == 2
    assert succeeded == 1
    assert failed == 1
    assert success_flags.count(False) == 1
    assert "RuntimeError" in error_types


def test_executor_enters_and_closes_handler_resources() -> None:
    async def scenario() -> tuple[bool, bool, list[str]]:
        handler = RecordingHandler()
        executor = AsyncTaskExecutor(worker_count=1)
        executor.register_handler(
            name="recording",
            handler=handler,
            matcher=lambda _task: True,
        )

        before = handler.is_open
        results = await executor.run([Task(id="r1", description="x", priority=1)])
        after = handler.is_open

        return before, after, [result.message for result in results]

    before, after, messages = asyncio.run(scenario())

    assert before is False
    assert after is False
    assert messages == ["handled:r1"]


def test_executor_works_concurrently() -> None:
    async def scenario() -> float:
        tasks = [
            Task(id="c1", description="x", priority=1),
            Task(id="c2", description="x", priority=1),
            Task(id="c3", description="x", priority=1),
        ]
        executor = AsyncTaskExecutor(worker_count=3)
        executor.register_handler(
            name="io",
            handler=SleepTaskHandler(delay_seconds=0.05),
            matcher=lambda _task: True,
        )

        start = perf_counter()
        await executor.run(tasks)
        return perf_counter() - start

    elapsed = asyncio.run(scenario())

    # Последовательная обработка заняла бы примерно 0.15 c, параллельная заметно меньше.
    assert elapsed < 0.12
