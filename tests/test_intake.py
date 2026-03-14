"""Тесты модуля приёма задач: сбор из нескольких источников через протокол."""

import pytest

from task_platform.intake import collect_tasks, collect_tasks_from_source


class LocalTestSource:
    def get_tasks(self) -> list[dict[str, object]]:
        return [{"id": "local-1", "payload": "x"}]


class AnotherSource:
    def get_tasks(self) -> list[dict[str, object]]:
        return [{"id": "local-2", "payload": "y"}]


class InvalidSource:
    pass


def test_collect_tasks_from_source_works_for_protocol_object() -> None:
    tasks = collect_tasks_from_source(LocalTestSource())
    assert tasks == [{"id": "local-1", "payload": "x"}]


def test_collect_tasks_from_source_rejects_invalid_object() -> None:
    with pytest.raises(TypeError):
        collect_tasks_from_source(InvalidSource())


def test_collect_tasks_aggregates_from_multiple_sources() -> None:
    tasks = collect_tasks([LocalTestSource(), AnotherSource()])

    assert len(tasks) == 2
    assert {task["id"] for task in tasks} == {"local-1", "local-2"}


def test_extensibility_new_source_works_without_code_change() -> None:
    class NewExperimentalSource:
        def get_tasks(self) -> list[dict[str, object]]:
            return [{"id": "exp-1", "payload": {"new": True}}]

    tasks = collect_tasks_from_source(NewExperimentalSource())

    assert tasks[0]["id"] == "exp-1"
