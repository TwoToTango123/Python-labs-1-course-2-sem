"""Демонстрация нововведений ЛР №3: очередь задач, итераторы и генераторы."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.task_platform import (
    InvalidTaskPriorityError,
    Task,
    TaskQueue,
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


def demo_task_queue_iteration() -> None:
    _separator("5) Протокол итерации TaskQueue")

    tasks = [
        Task("task-1", "Разработка API", 9, TaskStatus.READY),
        Task("task-2", "Написание тестов", 7, TaskStatus.IN_PROGRESS),
        Task("task-3", "Документация", 5, TaskStatus.DRAFT),
        Task("task-4", "Code review", 6, TaskStatus.READY),
        Task("task-5", "Рефакторинг", 8, TaskStatus.READY),
    ]

    queue = TaskQueue(tasks)

    print(f"Длина очереди: {len(queue)}")
    print(f"Очередь не пуста: {bool(queue)}")
    print(f"Представление: {repr(queue)}\n")

    print("Итерация 1 (использование for loop):")
    count = 0
    for task in queue:
        _print_task(task)
        count += 1
    print(f"Обойдено задач: {count}")

    print("\nИтерация 2 (множественный обход - возможен благодаря __iter__):")
    ids = [task.id for task in queue]
    print(f"IDs из второго обхода: {ids}")

    print("\nСовместимость со стандартными конструкциями Python:")
    print(f"  list(queue) выдаёт: {len(list(queue))} задач")
    print(f"  sum(queue) для подсчёта приоритетов: {sum(t.priority for t in queue)}")


def demo_task_queue_filtering() -> None:
    _separator("6) Ленивая фильтрация по статусу и приоритету")

    tasks = [
        Task("task-1", "Разработка API", 9, status=TaskStatus.READY),
        Task("task-2", "Написание тестов", 7, status=TaskStatus.IN_PROGRESS),
        Task("task-3", "Документация", 5, status=TaskStatus.DRAFT),
        Task("task-4", "Code review", 6, status=TaskStatus.READY),
        Task("task-5", "Рефакторинг", 8, status=TaskStatus.READY),
    ]

    queue = TaskQueue(tasks)

    print("Фильтр по статусу (READY):")
    ready_tasks = list(queue.filter_by_status(TaskStatus.READY))
    for task in ready_tasks:
        _print_task(task)

    print(f"\nФильтр по приоритету (priority >= 7):")
    high_priority = list(queue.filter_by_priority(min_priority=7))
    for task in high_priority:
        _print_task(task)

    print(f"\nКомбинированный фильтр (READY И приоритет >= 7):")
    ready_high = list(
        queue.filter_by_status_and_priority(
            statuses=[TaskStatus.READY], min_priority=7
        )
    )
    for task in ready_high:
        _print_task(task)

    print(f"\nУниверсальный фильтр (готовые задачи):")
    is_ready = list(queue.filter(lambda t: t.is_ready_for_execution))
    for task in is_ready:
        _print_task(task)

    print(f"\nОсобенность ленивой оценки:")
    print("  Генератор filter_by_status() не создаёт копию в памяти")
    filtered = queue.filter_by_status(TaskStatus.READY)
    print(f"  Тип: {type(filtered)}")
    first_task = next(filtered)
    _print_task(first_task)
    print("  Потреблена только первая задача, остальные не обработаны")


def demo_task_queue_transformations() -> None:
    _separator("7) Трансформации: map, chunk, take, skip, sorted_by")

    tasks = [
        Task("task-1", "Разработка API", 9, status=TaskStatus.READY),
        Task("task-2", "Написание тестов", 7, status=TaskStatus.IN_PROGRESS),
        Task("task-3", "Документация", 5, status=TaskStatus.DRAFT),
        Task("task-4", "Code review", 6, status=TaskStatus.READY),
        Task("task-5", "Рефакторинг", 8, status=TaskStatus.READY),
    ]

    queue = TaskQueue(tasks)

    print("map() - извлечение ID:")
    ids = list(queue.map(lambda t: t.id))
    print(f"  {ids}")

    print("\nmap() - сумма приоритетов:")
    total_priority = sum(queue.map(lambda t: t.priority))
    print(f"  Общий приоритет: {total_priority}")

    print("\nchunk() - разбиение на группы по 2:")
    for i, batch in enumerate(queue.chunk(2), 1):
        print(f"  Группа {i}: {[t.id for t in batch]}")

    print("\ntake(3) - первые 3 задачи:")
    first_three = list(queue.take(3))
    for task in first_three:
        _print_task(task)

    print("\nskip(2) - пропустить первые 2 задачи:")
    skipped = list(queue.skip(2))
    for task in skipped:
        _print_task(task)

    print("\nsorted_by(priority) - сортировка по приоритету:")
    sorted_queue = queue.sorted_by(lambda t: t.priority)
    for task in sorted_queue:
        print(f"  [{task.id}] priority={task.priority}")

    print("\nsorted_by(priority, reverse=True) - обратная сортировка:")
    sorted_desc = queue.sorted_by(lambda t: t.priority, reverse=True)
    for task in sorted_desc:
        print(f"  [{task.id}] priority={task.priority}")


def demo_task_queue_performance() -> None:
    _separator("8) Эффективность: большие объёмы и ленивая обработка")

    print("Создание очереди с 1000 задач...")
    large_tasks = [
        Task(f"task-{i}", f"Task {i}", (i % 10) + 1, status=TaskStatus.READY)
        for i in range(1000)
    ]
    queue = TaskQueue(large_tasks)

    print(f"Очередь создана: {repr(queue)}")

    print("\nЛенивый фильтр (не создаёт копию):")
    high_priority_filter = queue.filter(lambda t: t.priority >= 8)
    print(f"  Фильтр создан: {type(high_priority_filter)}")

    print("\nПотребление первых 5 элементов отфильтрованной последовательности:")
    count = 0
    for task in high_priority_filter:
        print(f"  [{task.id}] priority={task.priority}")
        count += 1
        if count >= 5:
            break

    print(f"\nОбработано только {count} задач из 1000 (остальные не загружались)")

    print("\nПакетная обработка с chunk():")
    batch_size = 100
    batch_count = 0
    for batch in queue.chunk(batch_size):
        batch_count += 1
    print(f"  Создано {batch_count} пакетов по {batch_size} задач")

    print("\nАналитика (подсчёт по статусам):")
    stats = {}
    for status in TaskStatus:
        count = sum(1 for _ in queue.filter_by_status(status))
        if count > 0:
            stats[status.value] = count
    print(f"  {stats}")


if __name__ == "__main__":
    print("Платформа обработки задач — Лабораторная работа №3")
    demo_model_and_properties()
    demo_descriptor_difference()
    demo_sources_and_intake()
    demo_serialization()
    demo_task_queue_iteration()
    demo_task_queue_filtering()
    demo_task_queue_transformations()
    demo_task_queue_performance()
    print("\nДемонстрация завершена.")
