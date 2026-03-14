"""Источник задач, загружающий данные из JSON-файла."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..runtime_validation import ensure_task_list
from ..task_types import Task


class FileTaskSource:
    """Загружает задачи из JSON-файла, содержащего список объектов задач."""

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)

    def get_tasks(self) -> list[Task]:
        with self._file_path.open("r", encoding="utf-8") as fh:
            raw_data: Any = json.load(fh)

        if not isinstance(raw_data, list):
            raise ValueError("JSON-источник должен содержать список задач")
        if not all(isinstance(item, dict) for item in raw_data):
            raise ValueError("Каждый элемент задачи должен быть объектом")

        return ensure_task_list(raw_data)
