"""Тесты FileTaskSource: чтение задач из JSON-файла."""

import json

import pytest

from task_platform.sources.file_source import FileTaskSource


def test_file_source_reads_valid_json(tmp_path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps([{"id": "1", "payload": {"x": 1}}, {"id": "2", "payload": 2}]),
        encoding="utf-8",
    )

    source = FileTaskSource(path)
    tasks = source.get_tasks()

    assert len(tasks) == 2
    assert tasks[0]["id"] == "1"


def test_file_source_rejects_non_list_json(tmp_path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({"id": "1", "payload": 1}), encoding="utf-8")

    source = FileTaskSource(path)
    with pytest.raises(ValueError):
        source.get_tasks()


def test_file_source_rejects_invalid_task_shape(tmp_path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps([{"id": "1"}]), encoding="utf-8")

    source = FileTaskSource(path)
    with pytest.raises(ValueError):
        source.get_tasks()


def test_file_source_raises_for_missing_file(tmp_path) -> None:
    source = FileTaskSource(tmp_path / "missing.json")

    with pytest.raises(FileNotFoundError):
        source.get_tasks()
