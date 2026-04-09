"""Тесты ApiStubTaskSource: API-заглушка как источник задач."""

import pytest

from task_platform.sources.api_stub_source import ApiStubTaskSource


def test_api_stub_source_returns_valid_tasks() -> None:
    source = ApiStubTaskSource(
        lambda: [{"id": "api-1", "description": "API task", "priority": 1}]
    )

    tasks = source.get_tasks()

    assert tasks[0].id == "api-1"
    assert tasks[0].description == "API task"


def test_api_stub_source_rejects_invalid_tasks() -> None:
    source = ApiStubTaskSource(lambda: [{"id": "api-1", "priority": 1}])

    with pytest.raises(ValueError):
        source.get_tasks()


def test_api_stub_source_propagates_fetcher_errors() -> None:
    def broken_fetcher() -> list[dict[str, object]]:
        raise RuntimeError("upstream down")

    source = ApiStubTaskSource(broken_fetcher)

    with pytest.raises(RuntimeError, match="upstream down"):
        source.get_tasks()
