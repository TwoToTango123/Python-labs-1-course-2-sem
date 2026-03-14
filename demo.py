"""Демонстрация работы платформы приёма задач (ЛР №1)."""

import json
import tempfile
from pathlib import Path

from src.task_platform import collect_tasks
from src.task_platform.sources import ApiStubTaskSource, FileTaskSource, GeneratorTaskSource


def _separator(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)


def demo_file_source() -> None:
    _separator("Источник из JSON-файла")

    tasks_data = [
        {"id": "file-1", "payload": {"action": "обработать заказ", "order_id": 101}},
        {"id": "file-2", "payload": {"action": "отправить уведомление", "user_id": 42}},
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(tasks_data, tmp, ensure_ascii=False)
        tmp_path = Path(tmp.name)

    source = FileTaskSource(tmp_path)
    tasks = source.get_tasks()
    tmp_path.unlink()

    print(f"Получено задач: {len(tasks)}")
    for task in tasks:
        print(f"  [{task['id']}] {task['payload']}")


def demo_generator_source() -> None:
    _separator("Программный генератор задач")

    source = GeneratorTaskSource(
        count=3,
        payload_factory=lambda i: {"action": "пересчитать статистику", "batch": i + 1},
        id_prefix="gen",
    )
    tasks = source.get_tasks()

    print(f"Получено задач: {len(tasks)}")
    for task in tasks:
        print(f"  [{task['id']}] {task['payload']}")


def demo_api_stub_source() -> None:
    _separator("API-заглушка")

    def fake_api() -> list[dict[str, object]]:
        return [
            {"id": "api-1", "payload": {"action": "проверить состояние ресурса", "url": "/health"}},
            {"id": "api-2", "payload": {"action": "обработать входящие данные", "source": "queue"}},
        ]

    source = ApiStubTaskSource(fake_api)
    tasks = source.get_tasks()

    print(f"Получено задач: {len(tasks)}")
    for task in tasks:
        print(f"  [{task['id']}] {task['payload']}")


def demo_intake() -> None:
    _separator("Единый модуль приёма (все источники)")

    sources = [
        FileTaskSource.__new__(FileTaskSource),  # пустышка — заменим на реальный
        GeneratorTaskSource(count=2, id_prefix="intake-gen"),
        ApiStubTaskSource(lambda: [{"id": "intake-api-1", "payload": "данные из API"}]),
    ]

    # Реальный файловый источник через временный файл
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump([{"id": "intake-file-1", "payload": "данные из файла"}], tmp, ensure_ascii=False)
        tmp_path = Path(tmp.name)

    sources[0] = FileTaskSource(tmp_path)
    all_tasks = collect_tasks(sources)
    tmp_path.unlink()

    print(f"Итого получено задач: {len(all_tasks)}")
    for task in all_tasks:
        print(f"  [{task['id']}] {task['payload']}")


if __name__ == "__main__":
    print("Платформа обработки задач — Лабораторная работа №1")
    demo_file_source()
    demo_generator_source()
    demo_api_stub_source()
    demo_intake()
    print("\nДемонстрация завершена.")
