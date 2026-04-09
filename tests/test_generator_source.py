"""Тесты GeneratorTaskSource: программная генерация задач."""

import pytest

from task_platform.sources.generator_source import GeneratorTaskSource
from task_platform.task_types import TaskStatus


def test_generator_source_produces_expected_count() -> None:
    source = GeneratorTaskSource(count=3)

    tasks = source.get_tasks()

    assert len(tasks) == 3
    assert [task.id for task in tasks] == ["generated-1", "generated-2", "generated-3"]


def test_generator_source_supports_custom_payload_factory() -> None:
    source = GeneratorTaskSource(
        count=2,
        description_factory=lambda i: f"task-{i}",
        priority_factory=lambda i: i + 1,
        status_factory=lambda i: TaskStatus.READY,
    )

    tasks = source.get_tasks()

    assert tasks[0].description == "task-0"
    assert tasks[1].priority == 2
    assert tasks[0].is_ready_for_execution


def test_generator_source_rejects_negative_count() -> None:
    with pytest.raises(ValueError):
        GeneratorTaskSource(count=-1)
