"""Демонстрация ЛР №4: асинхронный исполнитель задач."""

from __future__ import annotations

import asyncio
import logging

from src.task_platform import (
    AsyncTaskExecutor,
    FailingTaskHandler,
    SleepTaskHandler,
    Task,
    TaskStatus,
)


def _separator(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def _print_task(task: Task) -> None:
    print(
        f"  [{task.id}] {task.description!r} | priority={task.priority} "
        f"| status={task.status.value}"
    )


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _build_demo_tasks() -> list[Task]:
    return [
        Task(id="io-1", description="Синхронизация отчета", priority=5, status=TaskStatus.READY),
        Task(id="io-2", description="Обновление витрины", priority=3, status=TaskStatus.DRAFT),
        Task(id="fail-1", description="Провалить обработку", priority=8, status=TaskStatus.READY),
        Task(id="io-3", description="Проверка интеграции", priority=6, status=TaskStatus.READY),
    ]


async def _run_async_demo() -> None:
    _separator("1) Подготовка задач")
    tasks = _build_demo_tasks()
    for task in tasks:
        _print_task(task)

    _separator("2) Запуск асинхронного исполнителя")
    executor = AsyncTaskExecutor(worker_count=3)

    # Маршрут fail-* задач в обработчик-симулятор ошибки.
    executor.register_handler(
        name="failing-handler",
        handler=FailingTaskHandler(),
        matcher=lambda task: task.id.startswith("fail-"),
    )
    # Все остальные задачи обрабатываются I/O обработчиком.
    executor.register_handler(
        name="sleep-handler",
        handler=SleepTaskHandler(delay_seconds=0.2),
        matcher=lambda _task: True,
    )

    async with executor:
        for task in tasks:
            await executor.submit(task)
        await executor.wait_until_idle()

    _separator("3) Результаты выполнения")
    for result in executor.results:
        marker = "OK" if result.success else "ERR"
        print(
            f"  [{marker}] task={result.task_id} handler={result.handler_name} "
            f"message={result.message}"
        )

    _separator("4) Итоговые статусы задач")
    for task in tasks:
        _print_task(task)

    _separator("5) Статистика")
    print(f"  Всего: {executor.stats.total}")
    print(f"  Успешно: {executor.stats.succeeded}")
    print(f"  С ошибкой: {executor.stats.failed}")


if __name__ == "__main__":
    _configure_logging()
    print("Платформа обработки задач — Лабораторная работа №4")
    asyncio.run(_run_async_demo())
    print("\nДемонстрация завершена.")
