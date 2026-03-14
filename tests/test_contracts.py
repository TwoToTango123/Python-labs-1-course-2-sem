"""Тесты контракта TaskSourceProtocol и runtime_checkable."""

from task_platform.contracts import TaskSourceProtocol


class ValidSource:
    def get_tasks(self) -> list[dict[str, object]]:
        return [{"id": "1", "payload": {"x": 1}}]


class InvalidSource:
    def fetch(self) -> list[dict[str, object]]:
        return [{"id": "1", "payload": {"x": 1}}]


def test_runtime_protocol_accepts_valid_source() -> None:
    assert isinstance(ValidSource(), TaskSourceProtocol)


def test_runtime_protocol_rejects_invalid_source() -> None:
    assert not isinstance(InvalidSource(), TaskSourceProtocol)
