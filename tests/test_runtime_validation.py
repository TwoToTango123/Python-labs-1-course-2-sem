"""Тесты runtime-валидации: проверка контракта и формата задачи."""

import pytest

from task_platform.runtime_validation import ensure_task_list, is_task_source, validate_task_dict


class SourceLike:
    def get_tasks(self) -> list[dict[str, object]]:
        return [
            {
                "id": "ok",
                "description": "demo",
                "priority": 1,
                "status": "ready",
            }
        ]


def test_is_task_source_true_for_protocol_compatible_object() -> None:
    assert is_task_source(SourceLike())


def test_is_task_source_false_for_non_source() -> None:
    assert not is_task_source(object())


def test_validate_task_dict_returns_task() -> None:
    result = validate_task_dict(
        {"id": "task-1", "description": "demo", "priority": 2, "status": "ready"}
    )
    assert result.id == "task-1"
    assert result.is_ready_for_execution


@pytest.mark.parametrize(
    "task",
    [
        {"description": "demo", "priority": 1},
        {"id": "", "description": "demo", "priority": 1},
        {"id": 10, "description": "demo", "priority": 1},
        {"id": "ok", "priority": 1},
        {"id": "ok", "description": "demo", "priority": 0},
    ],
)
def test_validate_task_dict_rejects_invalid_payload(task: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_task_dict(task)


def test_ensure_task_list_validates_every_item() -> None:
    tasks = ensure_task_list(
        [
            {"id": "1", "description": "one", "priority": 1},
            {"id": "2", "description": "two", "priority": 2},
        ]
    )
    assert len(tasks) == 2


def test_ensure_task_list_fails_if_one_item_invalid() -> None:
    with pytest.raises(ValueError):
        ensure_task_list([{"id": "1", "description": "one", "priority": 1}, {"payload": 2}])
