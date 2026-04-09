"""Тесты доменной модели Task: дескрипторы, свойства и инварианты."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from task_platform.exceptions import (
    InvalidTaskDescriptionError,
    InvalidTaskIdError,
    InvalidTaskPriorityError,
    InvalidTaskStatusError,
    TaskStateTransitionError,
)
from task_platform.task_types import Task, TaskStatus


def test_task_initializes_and_exposes_safe_properties() -> None:
    task = Task(
        id="task-1",
        description="Implement descriptors",
        priority=3,
        status=TaskStatus.READY,
        created_at=datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc),
    )

    assert task.id == "task-1"
    assert task.description == "Implement descriptors"
    assert task.priority == 3
    assert task.status is TaskStatus.READY
    assert task.is_ready_for_execution
    assert not task.is_done


def test_task_rejects_invalid_values() -> None:
    with pytest.raises(InvalidTaskIdError):
        Task(id="", description="demo", priority=1)

    with pytest.raises(InvalidTaskDescriptionError):
        Task(id="task-1", description="", priority=1)

    with pytest.raises(InvalidTaskPriorityError):
        Task(id="task-1", description="demo", priority=0)

    with pytest.raises(InvalidTaskStatusError):
        Task(id="task-1", description="demo", priority=1, status="unknown")


def test_task_rejects_invalid_status_transition() -> None:
    task = Task(id="task-1", description="demo", priority=1)
    task.mark_done()

    with pytest.raises(TaskStateTransitionError):
        task.mark_in_progress()


def test_non_data_descriptor_can_be_shadowed_intentionally() -> None:
    task = Task(id="task-1", description="demo", priority=1)

    assert task.readiness is True

    task.__dict__["readiness"] = False

    assert task.readiness is False
    assert task.is_ready_for_execution is True


def test_task_round_trips_through_dict() -> None:
    created_at = datetime(2026, 4, 2, 12, 15, tzinfo=timezone.utc)
    task = Task(
        id="task-1",
        description="demo",
        priority=2,
        status="ready",
        created_at=created_at,
    )

    clone = Task.from_dict(task.to_dict())

    assert clone == task