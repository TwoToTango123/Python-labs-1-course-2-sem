"""Демонстрация нововведений ЛР №2: доменная модель Task и дескрипторы."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.task_platform import (
    InvalidTaskPriorityError,
    Task,
    TaskStateTransitionError,
    TaskStatus,
    collect_tasks,
)
from src.task_platform.sources import ApiStubTaskSource, FileTaskSource, GeneratorTaskSource


def _separator(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def _print_task(task: Task) -> None:
    print(
        f"  [{task.id}] {task.description!r} | priority={task.priority} "
        f"| status={task.status.value} | ready={task.is_ready_for_execution}"
    )


def demo_model_and_properties() -> None:
    _separator("1) Модель Task: дескрипторы, @property и инварианты")

    task = Task(id="demo-1", description="Подготовить отчёт", priority=3, status=TaskStatus.READY)
    _print_task(task)

    print("\nПереходы статусов:")
    task.mark_in_progress()
    _print_task(task)
    task.mark_done()
    _print_task(task)

    print("\nПроверка запрета некорректного состояния (done -> in_progress):")
    try:
        task.mark_in_progress()
    except TaskStateTransitionError as error:
        print(f"  Ожидаемая ошибка: {error}")

    print("\nПроверка валидации data descriptor (priority):")
    try:
        task.priority = 100
    except InvalidTaskPriorityError as error:
        print(f"  Ожидаемая ошибка: {error}")


def demo_descriptor_difference() -> None:
    _separator("2) Различие data и non-data descriptor")

    task = Task(id="demo-2", description="Проверить дескрипторы", priority=2)

    print("Data descriptor (priority) защищает значение:")
    try:
        task.__dict__["priority"] = "сломано"
    except Exception as error:  # noqa: BLE001
        print(f"  Нельзя подменить data descriptor через __dict__: {type(error).__name__}")
    print(f"  task.priority = {task.priority}")

    print("\nNon-data descriptor (readiness) можно затенить в __dict__:")
    print(f"  До затенения: task.readiness = {task.readiness}")
    task.__dict__["readiness"] = False
    print(f"  После затенения: task.readiness = {task.readiness}")
    print(
        "  Защищённое @property is_ready_for_execution остаётся корректным: "
        f"{task.is_ready_for_execution}"
    )


def demo_sources_and_intake() -> None:
    _separator("3) Источники задач и единый intake")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(
            [
                {
                    "id": "file-1",
                    "description": "Задача из файла",
                    "priority": 1,
                    "status": "ready",
                }
            ],
            tmp,
            ensure_ascii=False,
        )
        tmp_path = Path(tmp.name)

    file_source = FileTaskSource(tmp_path)
    gen_source = GeneratorTaskSource(
        count=2,
        id_prefix="gen",
        description_factory=lambda i: f"Сгенерированная задача #{i + 1}",
        priority_factory=lambda i: i + 2,
        status_factory=lambda i: TaskStatus.READY,
    )
    api_source = ApiStubTaskSource(
        lambda: [
            {
                "id": "api-1",
                "description": "Задача от API",
                "priority": 4,
                "status": "draft",
            }
        ]
    )

    all_tasks = collect_tasks([file_source, gen_source, api_source])
    tmp_path.unlink(missing_ok=True)

    print(f"Получено задач: {len(all_tasks)}")
    for task in all_tasks:
        _print_task(task)


def demo_serialization() -> None:
    _separator("4) Сериализация/десериализация модели")

    original = Task(id="ser-1", description="Сериализовать задачу", priority=5)
    payload = original.to_dict()
    restored = Task.from_dict(payload)

    print("Словарь после to_dict():")
    print(f"  {payload}")
    print(f"Восстановление из словаря эквивалентно: {restored == original}")


if __name__ == "__main__":
    print("Платформа обработки задач — Лабораторная работа №2")
    demo_model_and_properties()
    demo_descriptor_difference()
    demo_sources_and_intake()
    demo_serialization()
    print("\nДемонстрация завершена.")
