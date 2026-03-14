"""Тесты GeneratorTaskSource: программная генерация задач."""

import pytest

from task_platform.sources.generator_source import GeneratorTaskSource


def test_generator_source_produces_expected_count() -> None:
    source = GeneratorTaskSource(count=3)

    tasks = source.get_tasks()

    assert len(tasks) == 3
    assert [task["id"] for task in tasks] == ["generated-1", "generated-2", "generated-3"]


def test_generator_source_supports_custom_payload_factory() -> None:
    source = GeneratorTaskSource(count=2, payload_factory=lambda i: {"value": i * 10})

    tasks = source.get_tasks()

    assert tasks[0]["payload"] == {"value": 0}
    assert tasks[1]["payload"] == {"value": 10}


def test_generator_source_rejects_negative_count() -> None:
    with pytest.raises(ValueError):
        GeneratorTaskSource(count=-1)
